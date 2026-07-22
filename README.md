<div align="center">
  <img src="https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
</div>

<br>

<div align="center">
  <h1>AutoStack</h1>
  <p><strong>Production-Ready Docker Stack for AI Agents</strong></p>
  <p>Search, memory, browser, vector storage — one command deploy.</p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#stack">Stack</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## Screenshot

![AutoStack Dashboard](docs/screenshot.png)
*Self-hosted AI agent stack with search, memory, and vector storage.*

## Features

- **One Command Deploy** — `docker compose up -d` and you're ready.
- **Search Engine** — SearXNG for private web search.
- **Long-Term Memory** — Honcho for persistent agent memory.
- **Browser Automation** — Playwright for web interaction.
- **Vector Storage** — Qdrant for embeddings.
- **Privacy-Focused** — All data stays on your infrastructure.
- **CPU-Only** — No GPU required.
- **Production Ready** — Health checks and monitoring.

## Quick Start

```bash
git clone https://github.com/OneByJorah/AutoStack.git
cd AutoStack

cp .env.example .env
docker compose up -d
```

### Access Services

| Service | URL |
|---------|-----|
| SearXNG | http://localhost:8080 |
| Qdrant | http://localhost:6333 |
| Honcho | http://localhost:4000 |
| Browser | http://localhost:9222 |

## Stack Components

| Component | Purpose |
|-----------|---------|
| **SearXNG** | Privacy web search |
| **Qdrant** | Vector database |
| **Honcho** | Long-term memory |
| **Playwright** | Browser automation |
| **Redis** | Caching and queues |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_PORT` | `8080` | SearXNG port |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `HONCHO_PORT` | `4000` | Honcho port |
| `POSTGRES_DB` | `autostack` | Database name |

## Project Structure

```
AutoStack/
├── docker-compose.yml     # Main compose file
├── .env.example           # Environment template
├── scripts/
│   ├── setup.sh           # Initial setup
│   └── health-check.sh
└── README.md
```

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## Security

For security concerns, see [SECURITY.md](SECURITY.md). Please report vulnerabilities to **info@jorahone.com** — do not use public issues.

## License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>Production-ready AI agent stack.</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
