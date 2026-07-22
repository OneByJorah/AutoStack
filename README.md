# AutoStack

Production-ready Docker Compose stack for self-hosted AI agents — search, memory, browser automation, vector storage, and notes in one command.

![status](https://img.shields.io/badge/status-active-FFB300?style=flat-square)
![version](https://img.shields.io/badge/version-2.0.0-FFB300?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)

## Overview

AutoStack is a self-hosted, production-ready Docker Compose stack that bundles web search (SearXNG), long-term memory (Honcho + Qdrant), browser automation (Camofox), vector storage, and Obsidian note-taking into a single portable deployment. One command to bootstrap, health checks on every service, and an optional Portainer admin panel for visual container management.

## Features

- One-command bootstrap — `./scripts/bootstrap.sh` clones, configures, starts, and validates
- Zero secrets in git — `.env.example` documents every variable; `.env` is gitignored
- Health checks on every service — Docker healthchecks plus `./scripts/healthcheck.sh`
- Portainer CE admin panel — visual container management, logs, stats, RBAC
- CPU-first with optional GPU — runs on CPU; Ollama can target local or remote GPU hosts
- Extensible Compose blocks — add services by dropping in compose fragments
- CI/CD pipeline — GitHub Actions: lint, build, test, deploy on push
- Agent integration — skills for search, memory, browser, and notes

## Architecture / Tech Stack

| Layer | Stack |
|-------|-------|
| Runtime | Linux, Docker Compose v2 |
| Search | SearXNG + Camofox |
| Memory | Honcho (pgvector + Redis) + Qdrant |
| Notes | Obsidian Remote (web UI) |
| Admin | Portainer CE |
| CI/CD | GitHub Actions |

## Installation

```bash
git clone https://github.com/OneByJorah/AutoStack.git
cd AutoStack

cp .env.example .env  # Edit with your credentials
./scripts/bootstrap.sh
./scripts/healthcheck.sh localhost
```

### Prerequisites

- Docker 24+ and Docker Compose v2
- 8GB+ RAM, 50GB+ disk

## Configuration

| Variable | Description |
|----------|-------------|
| `HONCHO_DB_PASSWORD` | Honcho PostgreSQL password |
| `CAMOFOX_API_KEY` | Camofox browser automation key |
| `PORTAINER_ADMIN_PASSWORD` | Portainer admin password |

See `.env.example` for full options.

## License

MIT — see [LICENSE](LICENSE).

---
Part of the JorahOne / J1 ecosystem — self-hosted AI infrastructure without vendor lock-in.
