# arah

**Version:** v2.0
**Status:** Production Ready
**License:** MIT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

arah is a unified, production-ready Docker Compose deployment that consolidates self-hosted web search, long-term memory, browser automation, vector storage, and Obsidian note-taking under a single management plane. Designed for consumer hardware with Tailscale networking, the stack exposes services through direct ports with centralized administration.

**Core philosophy:** One stack, one IP, one admin panel, zero secrets in Git.

## Features

- ✅ **Single-command bootstrap** — `./bootstrap.sh` clones, configures, validates, and starts the stack
- ✅ **Zero secrets in Git** — `.env.example` documents all variables; `.env` is gitignored
- ✅ **Health checks on every service** — Docker healthchecks + `./scripts/healthcheck.sh`
- ✅ **Portainer admin panel** — Visual container management, logs, stats, backups, RBAC
- ✅ **CPU-first with GPU option** — Runs on CPU; optional upstream inference via Hermes config
- ✅ **Extensible Compose blocks** — Add services by dropping in compose fragments
- ✅ **CI/CD pipeline** — GitHub Actions: lint, build, test, deploy on push
- ✅ **Hermes Agent integration** — Skills for search, memory, browser, notes

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TAILSCALE NETWORK                            │
│  ollama host                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AR AH STACK                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  SEARCH & BROWSER              MEMORY & KNOWLEDGE          │  │
│  │  SearXNG (8080)                Honcho API (8081)           │  │
│  │  Selenium (4444)               Qdrant (6333)               │  │
│  │                                 PostgreSQL (5432)           │  │
│  │                                 Redis (6379)                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│        ┌─────────────────────┼─────────────────────┐             │
│        ▼                     ▼                     ▼             │
│  ┌───────────┐         ┌───────────┐         ┌───────────┐     │
│  │  NOTES    │         │  ADMIN    │         │ OPTIONAL  │     │
│  │ Obsidian  │         │ Portainer │         │ Headroom  │     │
│  │ (8083)    │         │ (9000)    │         │ (8787)    │     │
│  └───────────┘         └───────────┘         └───────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
- Hermes Agent → Local services (search, memory, browser) → Optional upstream LLM via Hermes config
- All services communicate over Docker internal network
- Single Tailscale IP exposes everything via direct ports

## Technology Stack

| Layer | Stack |
|-------|-------|
| Runtime | Linux (Ubuntu 22.04+), Docker Compose |
| Orchestration | Docker Compose v2, Bash bootstrap scripts |
| VCS | Git + GitHub (`github.com/OneByJorah/arah`) |
| Memory/Context | Honcho (pgvector + Redis), Qdrant |
| Search | SearXNG + Selenium |
| Notes | Obsidian Remote (Caddy reverse proxy) |
| Admin | **Portainer CE** (full container lifecycle, RBAC, backups) |
| Monitoring | **NOC Dashboard** (read-only unified health + Portainer stats) |
| Notifications | Telegram (J1-bot) |
| CI/CD | GitHub Actions (build, test, deploy) |

## Services

| Service | Port | Health Endpoint | Purpose |
|---------|------|-----------------|---------|
| **SearXNG** | 8080 | `/search?q=healthcheck&format=json` | Privacy-respecting metasearch |
| **Selenium** | 4444 | `/status` | Browser automation API |
| **Obsidian** | 8083 | `/` | Remote vault web UI |
| **Qdrant** | 6333 | `/readyz` | Vector database |
| **Honcho API** | 8081 | `/healthz` | Long-term memory for agents |
| **Honcho Redis** | 6379 | `redis-cli ping` | Cache layer |
| **Honcho Postgres** | 5432 | `pg_isready` | PostgreSQL + pgvector |
| **Portainer** | 9000/9443 | `/` | **Admin panel - full container mgmt** |

## Features

- ✅ **Single-command bootstrap** - `./scripts/bootstrap.sh` clones, configures, starts, validates
- ✅ **Zero-secrets in Git** - `.env.example` documents all vars; `.env` is gitignored
- ✅ **Health checks on every service** - Docker healthchecks + `./scripts/healthcheck.sh`
- ✅ **Portainer admin panel** - Visual container management, logs, stats, backups, RBAC
- ✅ **CPU-first with GPU option** - Runs on CPU; Ollama on Tailscale host for GPU inference
- ✅ **Extensible Compose blocks** - Add services by dropping in compose fragments
- ✅ **CI/CD pipeline** - GitHub Actions: lint, build, test, deploy on push
- ✅ **Hermes Agent integration** - Skills for search, memory, browser, notes

## Getting Started

### Prerequisites
- Docker 24+ & Docker Compose v2
- Tailscale (for multi-host Ollama access)
- 8GB+ RAM, 50GB+ disk

### Quick Start

```bash
# 1. Clone
git clone https://github.com/OneByJorah/arah.git
cd arah

# 2. Configure environment
cp .env.example .env
# Edit .env: set HONCHO_DB_PASSWORD, NEO4J_AUTH, CAMOFOX_API_KEY, etc.

# 3. One-command deploy
./bootstrap.sh

# 4. Verify
./scripts/healthcheck.sh localhost
```

### Manual Start

```bash
docker compose up -d
./scripts/healthcheck.sh localhost
```

### Access Points

| Interface | URL |
|-----------|-----|
| **NOC Dashboard** | http://localhost:9500 |
| **Portainer (Admin)** | http://localhost:9000 (HTTPS: 9443) |
| **SearXNG** | http://localhost:8080 |
| **Selenium** | http://localhost:4444 |
| **Obsidian** | http://localhost:8083 |
| **Honcho API** | http://localhost:8081 |
| **Qdrant** | http://localhost:6333 |
| **Ollama** | http://localhost:11434 |

## Environment Variables

All secrets in `.env` (never committed). See `.env.example` for full list.

| Variable | Purpose | Required |
|----------|---------|----------|
| `HONCHO_DB_PASSWORD` | PostgreSQL password for Honcho | Yes |
| `CAMOFOX_API_KEY` | Camofox auth key | Optional |
| `CAMOFOX_ADMIN_KEY` | Camofox admin key | Optional |
| `OBSIDIAN_VAULT_PATH` | Host path for Obsidian vault | Optional |
| `SERVER_IP` | Tailscale/local IP for docs | Optional |
| `NEO4J_AUTH` | Neo4j auth (if enabled) | Optional |
| `NOC_POLL_INTERVAL` | NOC Dashboard poll interval (seconds) | Optional |
| `PORTAINER_URL` | Portainer base URL for dashboard integration | Optional |
| `PORTAINER_API_KEY` | Portainer API key for container stats | Optional |
| `ENABLE_HEADROOM_MONITORING` | Enable Headroom services in dashboard | Optional |
| `OLLAMA_HOST` | Ollama Cloud hostname | Optional |
| `OLLAMA_PORT` | Ollama Cloud port | Optional |

## Service Management

```bash
# Start all
docker compose up -d

# Stop all
docker compose down

# View logs (all or specific)
docker compose logs -f
docker compose logs -f honcho

# Restart single service
docker compose restart honcho

# Health check
./scripts/healthcheck.sh localhost

# Full status
docker compose ps
```

### Optional overlays

```bash
# With Portainer + Headroom + NOC Dashboard
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dashboard.yml \
  -f docker-compose.portainer.yml \
  -f docker-compose.headroom.yml \
  up -d --build
```

### Env vars

| Variable | Purpose | Default |
|----------|---------|--------|
| `NOC_POLL_INTERVAL` | Seconds between polls | `10` |
| `PORTAINER_URL` | Portainer API base | empty (disabled) |
| `PORTAINER_API_KEY` | Portainer API key | empty (disabled) |
| `ENABLE_HEADROOM_MONITORING` | Monitor Headroom services | `false` |
| `OLLAMA_HOST` | Ollama container/host name | `ollama` |
| `OLLAMA_PORT` | Ollama port | `11434` |

## CI/CD & Deployment

**GitHub Actions** (`.github/workflows/ci-cd.yml`):

```yaml
# Triggers: push to main, PR to main
# Jobs:
#   1. lint       - hadolint, shellcheck, yamllint
#   2. build      - docker compose build (all services)
#   3. test       - spin up stack, run healthcheck.sh
#   4. deploy     - SSH to server, pull, restart (on main)
```

**Branch model:** `main` = stable; feature branches for changes.

**Deploy:** `git push origin main` → auto-deploys to configured host via SSH.

## Security

- **No secrets in Git** - `.env` in `.gitignore`; `.env.example` has placeholders
- **Portainer auth** - Admin user required on first access; RBAC for teams
- **Network isolation** - Services on internal Docker network; only explicitly mapped ports exposed
- **Tailscale** - All inter-host traffic encrypted; no public ports needed
- **Read-only mounts** - Config files mounted `:ro` where possible
- **Non-root containers** - Most services run as unprivileged users

## Project Structure

```
arah/
├── docker-compose.yml          # Core services
├── docker-compose.headroom.yml # Headroom monitoring overlay
├── docker-compose.portainer.yml # Portainer overlay
├── docker-compose.dashboard.yml # NOC dashboard overlay
├── .env.example                # Documented placeholders
├── .env                        # Local secrets (gitignored)
├── .gitignore
├── browser-search/             # Camofox + CloakBrowser helpers
│   ├── SKILL.md
│   ├── scripts/
│   └── docker/
├── obsidian-skills/            # Agent skills for Obsidian
│   └── skills/
│       ├── defuddle/
│       ├── json-canvas/
│       ├── obsidian-bases/
│       ├── obsidian-cli/
│       └── obsidian-markdown/
├── scripts/
│   ├── bootstrap.sh            # One-command deploy
│   ├── healthcheck.sh          # Validates all services
│   ├── init-honcho.sh          # Honcho alembic migrations
│   └── init-obsidian.sh        # Vault initialization
├── docs/
│   ├── SERVER_SETUP.md
│   ├── HERMES_SETUP.md
│   └── HONCHO_SETUP.md
├── honcho/
│   └── .env.honcho.example
├── live-manifest.json          # Server topology manifest
├── noc-dashboard/              # Read-only monitoring dashboard
│   ├── Dockerfile
│   ├── README.md
│   ├── backend/
│   └── frontend/
├── profiles/                   # Deployment profiles
│   ├── tailscale/
│   ├── cloudflare/
│   ├── local/
│   └── all/
└── tests/
    └── smoke.sh
```

## Hermes Integration

arah ships first-class Hermes Agent skills.

### Inline Commands

```bash
# Health check
bash scripts/healthcheck.sh localhost

# JSON search via SearXNG
curl -s 'http://localhost:8080/search?format=json&q=<query>&language=en'

# Browser automation via Selenium
curl -X POST http://localhost:4444/status

# Honcho memory operations
curl -X POST http://localhost:8081/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"text": "Remember this..."}'
```

## License

MIT

---

*arah is maintained by the J1 team. For enterprise support, contact J1admin.*
