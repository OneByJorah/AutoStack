"""
NOC Dashboard — AutoStack monitoring backend.

Polls every service in AutoStack over the internal Docker network using
the SAME health endpoints defined in docker-compose.yml / scripts/healthcheck.sh,
plus optional Portainer container stats if PORTAINER_URL is set.

This dashboard is READ-ONLY monitoring. It does not proxy traffic — every
service still exposes its own port/API directly, exactly as before.
"""
import asyncio
import os
import time
from collections import deque
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.static import StaticFiles


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

# Same services as docker-compose, with optional per-service host/port overrides:
#   SVC_<ID>_HOST / SVC_<ID>_PORT   (e.g. SVC_SEARXNG_HOST, SVC_QDRANT_PORT)
SERVICES = [
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

if env_bool("ENABLE_HEADROOM_MONITORING", True):
    SERVICES += [
        {"id": "headroom-proxy", "name": "Headroom Proxy", "host": "localhost", "port": 8787, "public_port": 8787,
         "kind": "http", "path": "/readyz", "group": "Headroom"},
        {"id": "headroom-qdrant", "name": "Headroom Qdrant", "host": "localhost", "port": 5333, "public_port": 5333,
         "kind": "http", "path": "/healthz", "group": "Headroom"},
        {"id": "headroom-neo4j", "name": "Headroom Neo4j", "host": "localhost", "port": 7474, "public_port": 7474,
         "kind": "http", "path": "/", "group": "Headroom"},
    ]


for svc in SERVICES:
    host_override = env_override_host(svc["id"])
    port_override = env_override_port(svc["id"])
    if host_override:
        svc["host"] = host_override
    if port_override:
        svc["port"] = port_override

PORTAINER_URL = os.getenv("PORTAINER_URL", "").rstrip("/")
PORTAINER_API_KEY = os.getenv("PORTAINER_API_KEY", "")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL_SECONDS", "10"))

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
        return {"up": False, "latency_ms": None, "error": str(exc)[:120]}


async def check_tcp(svc: dict) -> dict:
    start = time.perf_counter()
    try:
        fut = asyncio.open_connection(svc["host"], svc["port"])
        reader, writer = await asyncio.wait_for(fut, timeout=5.0)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {"up": True, "latency_ms": latency_ms}
    except Exception as exc:
        return {"up": False, "latency_ms": None, "error": str(exc)[:120]}


async def check_portainer() -> list:
    if not PORTAINER_URL:
        return []
    headers = {"X-API-Key": PORTAINER_API_KEY} if PORTAINER_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{PORTAINER_URL}/api/endpoints/1/docker/containers/json",
                                 headers=headers, params={"all": "true"})
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "name": c.get("Names", ["?"])[0].lstrip("/"),
                    "state": c.get("State"),
                    "status": c.get("Status"),
                    "image": c.get("Image"),
                }
                for c in data
            ]
    except Exception as exc:
        return [{"error": str(exc)[:200]}]


async def poll_once():
    async with httpx.AsyncClient() as client:
        results = {}
        tasks = []
        for svc in SERVICES:
            if svc["kind"] == "http":
                tasks.append(check_http(client, svc))
            else:
                tasks.append(check_tcp(svc))
        outcomes = await asyncio.gather(*tasks, return_exceptions=False)

    now = time.time()
    for svc, outcome in zip(SERVICES, outcomes):
        results[svc["id"]] = {
            **svc,
            **outcome,
            "checked_at": now,
        }
        state["history"][svc["id"]].append({
            "t": now,
            "up": outcome["up"],
            "latency_ms": outcome.get("latency_ms"),
        })

    results["_portainer"] = await check_portainer()
    state["services"] = results
    state["last_run"] = now


async def poll_loop():
    while True:
        try:
            await poll_once()
        except Exception:
            pass
        await asyncio.sleep(POLL_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_loop())
    yield
    task.cancel()


app = FastAPI(title="NOC AutoStack Dashboard", lifespan=lifespan)


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
            "ollama_host": os.getenv("OLLAMA_HOST", "ollama"),
            "ollama_port": int(os.getenv("OLLAMA_PORT", "11434")),
            "prod_hosts": os.getenv("PROD_HOSTS", ""),
        },
    })


@app.get("/api/healthz")
async def healthz():
    return {"ok": True}


app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")


if os.getenv("ENABLE_SETUP_API", "0").lower() in ("1", "true", "yes", "on"):
    import datetime
    import json
    import os
    import subprocess
    from pathlib import Path

    from fastapi import Request
    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(directory="/app/templates")

    REPO_ROOT = Path("/workspace")
    CF_DIR = Path("/cloudflared")
    COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"

    @app.get("/setup")
    async def setup_page(request: Request):
        return templates.TemplateResponse("setup.html", {"request": request})

    @app.post("/api/setup")
    async def apply_setup(request: Request):
        body = await request.json()
        mode = str(body.get("mode", "local")).strip()
        cf_host = str(body.get("cloudflare_hostname", "")).strip()
        cf_tunnel = str(body.get("cloudflare_tunnel", "")).strip()
        honcho_token = str(body.get("honcho_token", "")).strip()
        llm_key = str(body.get("llm_key", "")).strip()

        if mode not in {"local", "tailscale", "cloudflare", "all"}:
            return {"ok": False, "error": "Invalid mode"}

        profile = REPO_ROOT / "profiles" / mode / ".env"
        if not profile.exists():
            return {"ok": False, "error": f"Missing profile: {profile}"}

        payload = {
            "mode": mode,
            "cloudflare_hostname": cf_host,
            "cloudflare_tunnel": cf_tunnel,
            "honcho_token": honcho_token,
            "llm_key": llm_key,
            "applied_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        try:
            profile_text = profile.read_text()
            target_env = REPO_ROOT / ".env"
            target_env.write_text(profile_text + "\n")

            if honcho_token:
                target_env.write_text(target_env.read_text() + f"\nHONCHO_TOKEN={honcho_token}\n")
            if llm_key:
                target_env.write_text(target_env.read_text() + f"\nLLM_API_KEY={llm_key}\n")

            (REPO_ROOT / "setup-complete.json").write_text(json.dumps(payload, indent=2))

            if mode in ("cloudflare", "all") and cf_host and cf_tunnel:
                cf_credentials_dir = os.getenv("CF_CREDENTIALS_DIR", "/opt/autostack/.cloudflared")
                cf_host_ip = os.getenv("HOST_IP", "127.0.0.1")
                cf_content = f"""tunnel: {cf_tunnel}\ncredentials-file: {cf_credentials_dir}/{cf_tunnel}.json\ningress:\n  - hostname: {cf_host}\n    path: /honcho/*\n    service: http://{cf_host_ip}:8000\n  - hostname: {cf_host}\n    path: /qdrant/*\n    service: http://{cf_host_ip}:6333\n  - hostname: {cf_host}\n    path: /search/*\n    service: http://{cf_host_ip}:8080\n  - hostname: {cf_host}\n    path: /obsidian/*\n    service: http://{cf_host_ip}:8083\n  - hostname: {cf_host}\n    path: /costforge/*\n    service: http://{cf_host_ip}:8090\n  - hostname: {cf_host}\n    path: /noc/*\n    service: http://{cf_host_ip}:9500\n  - service: http_status:404\n"""
                CF_DIR.mkdir(parents=True, exist_ok=True)
                (CF_DIR / "config.yml").write_text(cf_content)

            apply_cmd = "bash scripts/apply-setup.sh"
            docker_socket = Path("/var/run/docker.sock")
            if docker_socket.exists():
                try:
                    proc = subprocess.run(
                        ["bash", "/workspace/scripts/apply-setup.sh"],
                        capture_output=True,
                        text=True,
                        timeout=180,
                    )
                    return {
                        "ok": proc.returncode == 0,
                        "mode": mode,
                        "apply_cmd": apply_cmd,
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                        "returncode": proc.returncode,
                    }
                except Exception as exc:
                    return {
                        "ok": False,
                        "mode": mode,
                        "apply_cmd": apply_cmd,
                        "error": str(exc),
                        "note": "Setup files were written. Run the apply command on the host.",
                    }
            else:
                return {
                    "ok": True,
                    "mode": mode,
                    "apply_cmd": apply_cmd,
                    "note": "Config written. Run the apply command on the host to restart services.",
                }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

