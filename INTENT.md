# INTENT.md — J1-PIPELINE Phase -1 (ORACLE)

**Repository:** `OneByJorah/AutoStack`  
**Analysis Date:** 2026-07-05  
**Analyst:** J1-PIPELINE ORACLE (read-only)  
**Status:** Intent Reconstructed

---

## What This System Does

### Technical Role

**AutoStack** (branded internally as **AutoStack v2.0**) is a **unified, production-ready Docker Compose deployment** that consolidates the full self-hosted infrastructure stack for an autonomous AI agent (Hermes Agent) under a single IP with centralized management. It bundles services across five functional categories:

| Category | Services | Ports |
|----------|----------|-------|
| **Search & Browser** | SearXNG (privacy metasearch), Camofox (stealth browser API), CloakBrowser (stealth browser for protected sites), Selenium WebAutomation | 8080, 9377, 9222, 4444 |
| **Memory & Knowledge** | Honcho API (long-term agent memory) + pgvector/Redis, Qdrant (vector database) | 8081, 5432, 6379, 6333 |
| **Notes & Docs** | Obsidian Remote (web-based vault) | 8083 |
| **Admin & Ops** | Portainer CE (full container lifecycle, RBAC, backups), NOC Dashboard (read-only unified health monitoring) | 9000/9443, 9500 |
| **Inference** | Ollama Cloud (optional, accessed over Tailscale from separate host) | 11434 |

### Operational Role

AutoStack is the **infrastructure substrate** for the JorahOne ecosystem's AI agent operations. It provides:

1. **Private web search** — SearXNG metasearch so Hermes can search the web without leaking queries to Google/Bing.
2. **Stealth browser automation** — Camofox + CloakBrowser for programmatic web browsing that evades bot detection (Cloudflare, Akamai, DataDome), enabling Hermes to interact with protected sites.
3. **Long-term agent memory** — Honcho (PostgreSQL + pgvector + Redis) for persistent conversation history, session context, vector embeddings, and multi-level reasoning (dialectic) across Hermes sessions.
4. **Vector storage** — Qdrant for similarity search and RAG-style retrieval.
5. **Graph memory** — Optional Headroom overlay (Neo4j + Qdrant) for structured knowledge graphs and Aphrodite proxy.
6. **Note-taking** — Obsidian Remote for persistent knowledge management accessible via Hermes skills.
7. **Unified monitoring** — NOC Dashboard polls every service's real health endpoints with latency sparklines, and optionally integrates Portainer container stats.
8. **Centralized admin** — Portainer for visual container lifecycle management (start/stop, logs, stats, volumes, networks, RBAC, backup).
9. **Setup automation** — CLI wizard + optional web setup API for four access modes (local, Tailscale, Cloudflare Tunnel, all).
10. **Hermes Agent skills** — The repo ships first-class Hermes Agent skills (`obsidian-skills/`, `browser-search/SKILL.md`) that teach Hermes how to use these services.

---

## Why This Was Built

### Real Problem

AI agents like Hermes need local infrastructure to operate autonomously — private search, persistent memory, browser automation, and note-taking — without depending on external SaaS providers that compromise privacy, introduce latency, or impose usage limits. Running these services individually requires significant manual configuration, and no single open-source stack existed that bundled them into a cohesive, production-ready deployment.

The web is also increasingly hostile to automation — Cloudflare, Akamai, DataDome, and other anti-bot systems block simple HTTP requests. A single browser automation tool is insufficient; the stack needs escalation from lightweight search → standard browsing → stealth browsing.

### Why Existing Tools Were Insufficient

- **SearXNG alone** provides search but no memory, browsing, or note-taking.
- **Honcho alone** provides agent memory but no search or browser.
- **Camofox/Playwright alone** provides browser automation but no memory or search.
- **Obsidian alone** provides notes but no agent integration.
- **Portainer alone** provides container management but no service-level health monitoring.
- **No existing project** combined all of these into a single `docker compose` stack with health checks, CI/CD, zero-secrets-in-git policy, multi-mode networking (local/Tailscale/Cloudflare), and Hermes Agent skill integration.
- **browser-search** (the search/browse skill) was originally a standalone project — it was folded into AutoStack to provide a complete, pre-integrated agent infrastructure package.

### What Triggered Development

The development of Hermes Agent (Nous Research's autonomous AI assistant) created an immediate need for a self-hosted "brain stack" — a production-ready environment where an AI agent can search the web, remember past conversations, browse websites programmatically, and maintain a knowledge base, all running on local consumer hardware (RTX 3060 12GB, Ubuntu 22.04+). The initial commit (`1350265` — "Initial full‑stack commit") established the full stack, and subsequent commits added setup automation, monitoring, security hardening, and ecosystem integration.

### JorahOne Ecosystem Fit

AutoStack is the **infrastructure layer** of the JorahOne ecosystem:

```
JorahOne Ecosystem
├── AutoStack     ← Infrastructure: search, memory, browser, notes, monitoring
├── Honcho                 ← Agent memory engine (upstream: plastic-labs/honcho)
├── Headroom               ← Graph memory / Aphrodite proxy (upstream: headroomlabs-ai/headroom)
├── CostForge              ← Cost tracking (planned, empty dir)
├── hermes-brain-stack     ← Brain stack integration (planned, empty dir)
├── Hermes Agent           ← AI agent that consumes all of the above
└── browser-search         ← Standalone search/browse skill (folded into AutoStack)
```

AutoStack provides the **self-hosted services** that Hermes Agent's web search, memory, browser, and note-taking capabilities depend on. Without AutoStack, Hermes would need external SaaS for every capability. With AutoStack, the entire agent infrastructure runs on local hardware behind Tailscale, with zero external dependencies for core operations.

---

## Operational Classification

**Classification: PRODUCTION**

Evidence:

- **Version:** v2.0, explicitly labeled "Production Ready" in README.
- **Health checks:** Every service has Docker healthchecks with retry logic; `scripts/healthcheck.sh` validates all 9+ services.
- **CI/CD:** GitHub Actions pipeline (CodeQL weekly scanning), Dependabot configured for pip/npm/docker/github-actions.
- **Security posture:** Zero secrets in git (`.env` gitignored, `.env.example` has placeholders), non-root containers, read-only mounts, network isolation, Tailscale encryption.
- **Security audits:** Two security commits in git history — `7fac97d` redacted hardcoded Tailscale IPs, `a06767a` sanitized j1admin email references.
- **Monitoring:** NOC Dashboard provides real-time health polling with latency sparklines and Portainer integration.
- **Backup:** Portainer backup/restore, Docker volumes for persistent data (honcho-pgdata, honcho-redis-data, portainer-data).
- **Deployment automation:** Bootstrap script, setup wizard (CLI + web), apply script, four access modes (local/Tailscale/Cloudflare/all).
- **Live deployment:** `live-manifest.json` documents an active production deployment with all services verified as "up" on a Tailscale network.
- **Community readiness:** CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, issue templates (bug + feature), PR template, Dependabot config, MIT license.

---

## Key Architectural Decisions

1. **Single IP, direct ports** — No reverse proxy or API gateway. Every service exposes its own port directly. The NOC Dashboard is read-only monitoring, not a proxy. This simplifies debugging and avoids a single point of failure.

2. **Compose overlays** — Honcho, Headroom, Portainer, and NOC Dashboard are separate compose files that compose on top of the base `docker-compose.yml`. Users opt in to what they need. This keeps the base stack lean and allows independent lifecycle management.

3. **Zero secrets in git** — All secrets go in `.env` (gitignored). `.env.example` documents the schema. Profile-based `.env` files under `profiles/` are selected at setup time. The repo has been audited to remove hardcoded IPs and emails.

4. **Hermes-first design** — The entire stack is designed to be consumed by Hermes Agent. Skills, API endpoints, and config examples all target Hermes. The `browser-search` skill was folded in from a standalone project to provide pre-integrated search/browse capabilities.

5. **CPU-first with GPU option** — Runs on CPU by default; GPU inference (Ollama) is accessed over Tailscale from a separate host. This keeps the stack deployable on consumer hardware.

6. **Multi-mode networking** — Four access modes (local, Tailscale, Cloudflare Tunnel, all) selected at setup time via CLI wizard or web UI. Cloudflare Tunnel config is generated dynamically with per-service path routing.

7. **Portainer as admin panel** — Rather than building a custom admin UI, the stack uses Portainer CE for container lifecycle management. This was a deliberate decision to avoid reinventing container management — Portainer provides RBAC, logs, stats, backups, and stack deployment out of the box.

8. **Three-tier browser escalation** — SearXNG (fast search) → Camofox (REST API browser for standard sites) → CloakBrowser (stealth Chromium for anti-bot protected sites). The agent automatically escalates when a tool fails.

---

## Repository Structure

```
AutoStack/
├── docker-compose.yml              # Base: SearXNG, Qdrant, Honcho, Obsidian, WebAutomation
├── docker-compose.honcho.yml       # Overlay: Honcho API + pgvector + Redis
├── docker-compose.headroom.yml     # Overlay: Headroom proxy + Qdrant + Neo4j
├── docker-compose.portainer.yml     # Overlay: Portainer CE admin panel
├── bootstrap.sh                    # One-command deploy
├── live-manifest.json              # Live deployment topology (Tailscale IPs redacted)
├── scripts/
│   ├── bootstrap.sh                # Pull images, start stack, healthcheck
│   ├── healthcheck.sh              # Validates all services via HTTP/TCP
│   ├── setup-wizard.sh             # CLI mode selection + Cloudflare config
│   ├── apply-setup.sh              # Applies profile + Cloudflare config + restart
│   ├── init-honcho.sh              # Honcho env + config initialization
│   ├── init-obsidian.sh            # Obsidian vault initialization
│   ├── init-headroom.sh            # Headroom env initialization
│   ├── install.sh                  # Python venv setup
│   └── install-browser-search.sh   # npm install for browser-search
├── docs/
│   ├── SERVER_SETUP.md             # Server prerequisites and install
│   ├── HERMES_SETUP.md             # Hermes Agent config for local services
│   ├── HONCHO_SETUP.md             # Honcho submodule + API key setup
│   ├── HEADROOM_SETUP.md           # Headroom overlay setup
│   ├── SETUP_WIZARD.md             # CLI + web setup wizard docs
│   ├── MAINTENANCE.md              # Restart, update, backup commands
│   └── hermes.md                   # Hermes service interaction reference
├── profiles/
│   ├── local/.env.example          # Local-only mode env
│   ├── tailscale/.env              # Tailscale mode env
│   ├── cloudflare/.env             # Cloudflare Tunnel mode env
│   └── all/.env                    # All modes combined env
├── browser-search/                 # Standalone search/browse skill package
│   ├── SKILL.md                    # Hermes Agent skill for search/browse
│   ├── README.md                   # Multi-language README (11 languages)
│   ├── package.json                # npm package (CloakBrowser)
│   ├── scripts/                    # Camofox + CloakBrowser scripts
│   └── docker/                     # Docker setup docs
├── obsidian-skills/                # Hermes Agent skills for Obsidian
│   ├── obsidian-cli/SKILL.md
│   ├── obsidian-markdown/SKILL.md
│   ├── obsidian-bases/SKILL.md
│   ├── defuddle/SKILL.md
│   └── json-canvas/SKILL.md
├── noc-dashboard/                  # FastAPI monitoring dashboard
│   ├── Dockerfile
│   ├── docker-compose.dashboard.yml
│   ├── docker-compose.portainer.yml
│   ├── backend/app.py              # Main dashboard backend
│   ├── backend/standalone.py       # Standalone (no Docker) version
│   ├── frontend/index.html         # Amber-themed monitoring UI
│   └── templates/setup.html        # Web setup wizard UI
├── honcho/
│   ├── config.toml                 # Honcho LLM provider config
│   ├── honcho-config.json          # Hermes Honcho client config
│   └── .env.honcho.example         # Honcho API key template
├── headroom/
│   └── headroom-config.example     # Headroom runtime config example
├── searxng/
│   └── settings.yml                # SearXNG config (JSON format, public_instance: false)
├── CostForge/                      # Cost tracking (empty, planned)
├── hermes-brain-stack/             # Brain stack integration (empty, planned)
├── tests/
│   └── smoke.sh                    # End-to-end smoke test
├── test_results.txt                # Historical test output
├── .github/
│   ├── workflows/codeql.yml        # CodeQL weekly security scan
│   ├── dependabot.yml              # Weekly dependency updates (pip, npm, docker, actions)
│   ├── ISSUE_TEMPLATE/bug_report.md
│   ├── ISSUE_TEMPLATE/feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── CODE_OF_CONDUCT.md              # Contributor Covenant v2.1
├── CONTRIBUTING.md                 # Contribution guidelines
├── SECURITY.md                     # 90-day disclosure policy
├── LICENSE                         # MIT
├── .gitignore                      # .env, __pycache__, node_modules, etc.
└── README.md                       # AutoStack v2.0 README
```

---

## Notes

- **Naming resolved:** The repo's GitHub name is now **AutoStack** matching the README brand **AutoStack v2.0**.
- **Empty directories:** `CostForge/` and `hermes-brain-stack/` exist but are empty — planned future additions for cost tracking and brain stack integration.
- **Missing submodules:** `vendor/honcho` and `vendor/headroom` are referenced in compose files but not currently checked into the repo. The compose files reference `context: vendor/honcho` and `context: vendor/headroom` for building from source, but these directories don't exist.
- **Portainer service gap:** Portainer was referenced in the README and healthcheck script but had no compose definition until `docker-compose.portainer.yml` was added (noted in the file's own comment: "was never actually defined as a service — this fills that gap").
- **Dependabot config drift:** Dependabot is configured for `pip` at directory `/`, but there is no `requirements.txt` at the repo root — only in `noc-dashboard/backend/`. The `npm` and `docker` ecosystems are correctly configured. This is a minor template vestige.
- **Security audit history:** Two security commits in git history — `7fac97d` (redacted hardcoded Tailscale IPs) and `a06767a` (sanitized j1admin email references). This is a positive maturity signal.
- **browser-search provenance:** The `browser-search/` subdirectory is a standalone open-source project (MIT, 11-language README) that was folded into AutoStack. It has its own `package.json`, `SKILL.md`, and multi-language documentation.
- **Live deployment:** `live-manifest.json` documents a real production deployment with Tailscale networking, all services verified as "up", and a `CostForge` service listed as "pending".
- **Honcho config.toml** is extensively configured with multi-tier LLM providers (vllm primary, custom backup), dialectic reasoning levels (minimal through max), memory consolidation ("dream"), and session summarization — all targeting Hermes Agent integration.
