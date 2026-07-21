<div align="center">

# AutoStack

**Production-ready Docker Compose stack for self-hosted AI agents.**

[![CI](https://github.com/OneByJorah/AutoStack/actions/workflows/ci.yml/badge.svg)](https://github.com/OneByJorah/AutoStack/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-2496ED?style=flat-square)
![Version](https://img.shields.io/badge/version-2.0.0-2496ED?style=flat-square)

</div>

AutoStack bundles web search, long-term memory, browser automation, vector storage, and Obsidian note-taking into a single, portable Docker Compose deployment.

---

## Features

- **One-command bootstrap** — `./scripts/bootstrap.sh` clones, configures, starts, and validates
- **Zero secrets in git** — `.env.example` documents every variable; `.env` is gitignored
- **Health checks on every service** — Docker healthchecks plus `./scripts/healthcheck.sh`
- **Portainer admin panel** — Visual container management, logs, stats, backups, RBAC
- **CPU-first with optional GPU** — Runs on CPU; Ollama can target a local or remote GPU host
- **Extensible Compose blocks** — Add services by dropping in compose fragments
- **CI/CD pipeline** — GitHub Actions: lint, build, test, deploy on push
- **Agent integration** — Skills for search, memory, browser, and notes

---

## Technology Stack

| Layer | Stack |
|-------|-------|
| Runtime | Linux, Docker Compose v2 |
| Search | SearXNG + Camofox |
| Memory | Honcho (pgvector + Redis) + Qdrant |
| Notes | Obsidian Remote (web UI) |
| Admin | Portainer CE |
| CI/CD | GitHub Actions |

---

## Quick Start

### Prerequisites

- Docker 24+ & Docker Compose v2
- 8GB+ RAM, 50GB+ disk

### Deploy

```bash
# 1. Clone
git clone https://github.com/OneByJorah/AutoStack.git
cd AutoStack

# 2. Configure environment
cp .env.example .env
# Edit .env: set HONCHO_DB_PASSWORD, CAMOFOX_API_KEY, etc.

# 3. One-command deploy
./scripts/bootstrap.sh

# 4. Verify
./scripts/healthcheck.sh localhost
```

### Access Points

| Interface | URL |
|-----------|-----|
| NOC Dashboard | http://localhost:9500 |
| Portainer (Admin) | http://localhost:9000 |
| SearXNG | http://localhost:8080 |
| Camofox | http://localhost:9377 |
| Obsidian | http://localhost:8083 |
| Honcho API | http://localhost:8081 |
| Qdrant | http://localhost:6333 |
| Ollama | http://localhost:11434 |

---

## Environment Variables

All secrets live in `.env` (never committed). See `.env.example` for the full list.

| Variable | Purpose | Default |
|----------|---------|---------|
| `HOST_IP` | Host IP used by tunnel configs and docs | `127.0.0.1` |
| `HONCHO_IMAGE` | Honcho container image | `ghcr.io/onebyjorah/honcho:latest` |
| `HONCHO_DB_PASSWORD` | PostgreSQL password for Honcho | required |
| `HONCHO_TOKEN` | Honcho API auth token | required |
| `CAMOFOX_API_KEY` | Camofox auth key | optional |
| `CAMOFOX_ADMIN_KEY` | Camofox admin key | optional |
| `OBSIDIAN_VAULT_PATH` | Host path for Obsidian vault | `/opt/autostack/ObsidianVault` |
| `CF_CREDENTIALS_DIR` | Cloudflare Tunnel credentials directory | `/opt/autostack/.cloudflared` |
| `OLLAMA_HOST` | Ollama container/host name | `ollama:11434` |
| `LOG_LEVEL` | Log verbosity | `INFO` |

---

## Service Management

```bash
# Start all
docker compose up -d

# Stop all
docker compose down

# View logs
docker compose logs -f

# Restart a single service
docker compose restart honcho

# Health check
./scripts/healthcheck.sh localhost
```

---

## Agent Integration

AutoStack ships first-class agent skills under `obsidian-skills/`.

```bash
# Health check
cd /opt/autostack && bash scripts/healthcheck.sh localhost

# JSON search via SearXNG
curl -s 'http://localhost:8080/search?format=json&q=<query>&language=en'

# Browser automation via Camofox
curl -X POST http://localhost:9377/api/v1/browse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "action": "screenshot"}'

# CloakBrowser for protected sites
cd /opt/autostack/browser-search && node scripts/cloak/cloak-fetch.mjs "https://example.com"

# Honcho memory operations
curl -X POST http://localhost:8081/api/v1/memory \
  -H "Authorization: Bearer $HONCHO_TOKEN" \
  -d '{"text": "Remember this..."}'
```

---

## Project Structure

```
AutoStack/
├── docker-compose.yml          # Core services
├── .env.example                # Documented placeholders
├── .env                        # Local secrets (gitignored)
├── .gitignore
├── browser-search/             # Camofox + CloakBrowser helpers
├── obsidian-skills/            # Agent skills for Obsidian
├── scripts/                    # Bootstrap, healthcheck, setup
├── noc-dashboard/              # Read-only monitoring dashboard
├── .github/workflows/          # CI/CD pipelines
└── README.md
```

---

## CI/CD

GitHub Actions in `.github/workflows/`:

- `ci.yml` — shellcheck, yamllint, Docker Compose validation, smoke test
- `codeql.yml` — security analysis

Branch model: `main` is stable; open feature branches for work in progress.

---

## Security

- No secrets in git — `.env`, `.env.local` in `.gitignore`
- Network isolation — internal Docker network; only mapped ports exposed
- Read-only mounts — config files mounted `:ro` where possible
- Non-root containers — most services run as unprivileged users
- Report vulnerabilities to **info@jorahone.com**

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

MIT © Jhonattan L. Jimenez
