<div align="center">

![AutoStack banner](docs/assets/banner.svg)

# AutoStack

**Production-ready Docker Compose stack for self-hosted AI agents** — SearXNG, Qdrant, Honcho, Playwright, one command deploy.

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker_Compose-Ready-2496ED?logo=docker&logoColor=fff)](https://docker.com)
[![CPU](https://img.shields.io/badge/CPU--Only-No%20GPU%20Required-brightgreen)]()
[![Privacy](https://img.shields.io/badge/Privacy-Self--Hosted-blue)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)](CONTRIBUTING.md)

</div>

---

<p align="center">
  <img src="docs/screenshots/noc-dashboard-full.png" alt="AutoStack NOC dashboard preview" width="90%">
</p>

---

## What It Does

AutoStack is a **one-command AI infrastructure stack** that deploys SearXNG (private search), Qdrant (vector DB), Honcho (agent memory), and Selenium browser automation — all self-hosted, CPU-only, privacy-focused.

## Quick Start

```bash
git clone https://github.com/OneByJorah/AutoStack.git
cd AutoStack
cp .env.example .env
docker compose up -d
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **SearXNG** | http://localhost:8080 | Private web search |
| **Qdrant** | http://localhost:6333 | Vector database |
| **Honcho** | http://localhost:8081 | Agent memory |
| **Obsidian** | http://localhost:8083 | Vault UI |
| **Selenium** | http://localhost:4444 | Browser automation |

## Features

- **One Command Deploy** — docker compose up -d and you're ready
- **Private Search** — SearXNG with 100+ providers, no tracking
- **Agent Memory** — Honcho for persistent long-term memory
- **Browser Automation** — Selenium + optional Camofox stealth browser
- **Vector Storage** — Qdrant for embeddings and semantic search
- **Privacy-Focused** — All data stays on your infrastructure
- **CPU-Only** — No GPU required
- **Production Ready** — Health checks, monitoring, restart policies

## Stack Components

| Component | Purpose | Port |
|-----------|---------|------|
| **SearXNG** | Privacy web search engine | :8080 |
| **Qdrant** | Vector database for embeddings | :6333 |
| **Honcho** | Long-term agent memory | :8081 |
| **Selenium** | Chrome browser automation | :4444 |
| **Obsidian** | Caddy-served vault UI | :8083 |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| HOST_IP | 127.0.0.1 | Host IP for tunnel ingress |
| QDRANT_BIND | 127.0.0.1 | Qdrant bind address |
| OBSIDIAN_VAULT_PATH | /opt/autostack/ObsidianVault | Vault host path |

## Use Cases

1. **AI Developers** — Quick local stack for building AI agents
2. **Privacy Advocates** — Self-hosted alternative to cloud AI
3. **Researchers** — Experiment with RAG and vector search
4. **MSPs** — Deploy AI capabilities for internal tools

## License

MIT © Jhonattan L. Jimenez (OneByJorah)

---

<p align="center">Built with 🌴 by <a href="https://github.com/OneByJorah">OneByJorah</a> · <a href="https://jorahone.com">jorahone.com</a></p>
