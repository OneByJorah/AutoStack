"""
J1-NOC Dashboard — Standalone version (no Docker required).
Mounts static files from local frontend/ dir and adds localhost fallback
for services so health checks work even without Docker network.
"""
import asyncio
import os
import socket
import time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_override_host(svc_id: str) -> str | None:
    val = os.getenv(f"SVC_{svc_id.upper().replace('-', '_')}_HOST")
    return val.strip() if val else None


def env_override_port(svc_id: str) -> int | None:
    val = os.getenv(f"SVC_{svc_id.upper().replace('-', '_')}_PORT")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None

HISTORY_LEN = 20
BASE_DIR = Path(__file__).parent.resolve()

# Services, with optional per-service host/port overrides:
#   SVC_<ID>_HOST / SVC_<ID>_PORT   (e.g. SVC_SEARXNG_HOST, SVC_QDRANT_PORT)
DEFAULT_SERVICES = [
    {"id": "searxng", "name": "SearXNG", "host": "localhost", "port": 8080, "public_port": 8080,
     "kind": "http", "path": "/search?q=healthcheck&format=json", "group": "Search & Browser"},
    {"id": "camofox", "name": "Camofox", "host": "localhost", "port": 9377, "public_port": 9377,
     "kind": "http", "path": "/health", "group": "Search & Browser"},
    {"id": "cloakbrowser", "name": "CloakBrowser", "host": "localhost", "port": 9222, "public_port": 9222,
     "kind": "http", "path": "/json/version", "group": "Search & Browser"},
    {"id": "obsidian", "name": "Obsidian Remote", "host": "localhost", "port": 8080, "public_port": 8083,
     "kind": "http", "path": "/", "group": "Notes & Docs"},
    {"id": "qdrant", "name": "Qdrant", "host": "localhost", "port": 6333, "public_port": 6333,
     "kind": "http", "path": "/readyz", "group": "Memory & Knowledge"},
    {"id": "honcho", "name": "Honcho API", "host": "localhost", "port": 8081, "public_port": 8081,
     "kind": "http", "path": "/healthz", "group": "Memory & Knowledge"},
    {"id": "honcho-db", "name": "Honcho DB (Postgres)", "host": "localhost", "port": 5432, "public_port": None,
     "kind": "tcp", "group": "Memory & Knowledge"},
    {"id": "honcho-redis", "name": "Honcho Redis", "host": "localhost", "port": 6379, "public_port": None,
     "kind": "tcp", "group": "Memory & Knowledge"},
    {"id": "ollama", "name": "Ollama Cloud", "host": "localhost", "port": 11434, "public_port": 11434,
     "kind": "http", "path": "/api/tags", "group": "Inference"},
]

SERVICES = []
for svc in DEFAULT_SERVICES:
    host_override = env_override_host(svc["id"])
    port_override = env_override_port(svc["id"])
    SERVICES.append({
        **svc,
        "host": host_override or svc["host"],
        "port": port_override or svc["port"],
    })

if env_bool("ENABLE_HEADROOM_MONITORING", False):
    SERVICES += [
        {"id": "headroom-proxy", "name": "Headroom Proxy", "host": "localhost", "port": 8787, "public_port": 8787,
         "kind": "http", "path": "/readyz", "group": "Headroom"},
        {"id": "headroom-qdrant", "name": "Headroom Qdrant", "host": "localhost", "port": 5333, "public_port": 5333,
         "kind": "http", "path": "/healthz", "group": "Headroom"},
        {"id": "headroom-neo4j", "name": "Headroom Neo4j", "host": "localhost", "port": 7474, "public_port": 7474,
         "kind": "http", "path": "/", "group": "Headroom"},
    ]

PORTAINER_URL = os.getenv("PORTAINER_URL", "").rstrip("/")
PORTAINER_API_KEY = os.getenv("PORTAINER_API_KEY", "")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL_SECONDS", "10"))
PORT = int(os.getenv("PORT", "9500"))

state = {
    "services": {},
    "history": {s["id"]: deque(maxlen=HISTORY_LEN) for s in SERVICES},
    "last_run": None,
}


async def check_http(client: httpx.AsyncClient, svc: dict) -> dict:
    url = f"http://{svc['host']}:{svc['port']}{svc.get('path', '/')}"
    start = time.perf_counter()
    try:
        r = await client.get(url, timeout=5.0)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        up = r.status_code < 500
        return {"up": up, "latency_ms": latency_ms, "code": r.status_code}
    except Exception as exc:
        return {"up": False, "latency_ms": None, "error": str(exc)[:80]}


async def check_tcp(svc: dict) -> dict:
    start = time.perf_counter()
    try:
        fut = asyncio.open_connection(svc["host"], svc["port"])
        reader, writer = await asyncio.wait_for(fut, timeout=3.0)
        writer.close()
        await writer.wait_closed()
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {"up": True, "latency_ms": latency_ms, "code": None}
    except Exception as exc:
        return {"up": False, "latency_ms": None, "error": str(exc)[:80]}


async def check_portainer() -> list:
    if not PORTAINER_URL:
        return []
    url = f"{PORTAINER_URL}/api/endpoints/1/docker/containers/json"
    try:
        async with httpx.AsyncClient() as c:
            headers = {"X-API-Key": PORTAINER_API_KEY} if PORTAINER_API_KEY else {}
            r = await c.get(url, headers=headers, timeout=5.0)
            if r.status_code != 200:
                return [{"error": f"HTTP {r.status_code}"}]
            data = r.json()
            return [{"name": ctn.get("Names", [""])[0].lstrip("/"),
                     "state": ctn.get("State"),
                     "status": ctn.get("Status"),
                     "image": ctn.get("Image"),
                     "id": ctn.get("Id", "")[:12]} for ctn in data]
    except Exception as exc:
        return [{"error": str(exc)[:120]}]


async def poll_once():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = []
        for svc in SERVICES:
            if svc["kind"] == "http":
                tasks.append(check_http(client, svc))
            else:
                tasks.append(check_tcp(svc))
        results = await asyncio.gather(*tasks)

    for svc, res in zip(SERVICES, results):
        state["services"][svc["id"]] = {"id": svc["id"], **res}
        state["history"][svc["id"]].append({
            "time": time.time(),
            "up": res["up"],
            "latency_ms": res.get("latency_ms"),
        })

    state["services"]["_portainer"] = await check_portainer()
    state["last_run"] = time.time()


async def poll_loop():
    while True:
        await poll_once()
        await asyncio.sleep(POLL_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_loop())
    yield
    task.cancel()


app = FastAPI(title="J1-NOC StackDeploy Dashboard", lifespan=lifespan)


@app.get("/api/status")
async def api_status():
    services = {k: v for k, v in state["services"].items() if k != "_portainer"}
    history = {k: list(v) for k, v in state["history"].items()}
    return JSONResponse({
        "last_run": state["last_run"],
        "poll_interval": POLL_INTERVAL,
        "services": services,
        "history": history,
        "portainer": {
            "configured": bool(PORTAINER_URL),
            "containers": state["services"].get("_portainer", []),
        },
        "prod": {
            "configured": True,
            "ollama_host": os.getenv("OLLAMA_HOST", "localhost"),
            "ollama_port": int(os.getenv("OLLAMA_PORT", "11434")),
            "prod_hosts": os.getenv("PROD_HOSTS", ""),
        }
    })


@app.get("/api/healthz")
async def healthz():
    return {"ok": True}


# Serve static frontend from local directory
static_dir = str(BASE_DIR.parent / "frontend")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "NOC Dashboard backend running", "static_dir": static_dir, "port": PORT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
