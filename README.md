<div align="center">

![AutoStack banner](docs/assets/banner.svg)

# AutoStack

Production-ready Docker Compose stack for self-hosted AI agents

![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Language](https://img.shields.io/badge/language-JavaScript-blue)
</div>

---

<p align="center">
  <img src="docs/assets/screenshot.png" alt="AutoStack preview" width="90%">
</p>

<br>

---

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

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## 🔒 Security

Found a vulnerability? Please follow our [Security Policy](SECURITY.md) and report privately to `security@jorahone.com`.

## 📄 License

[MIT License](LICENSE) © Jhonattan L. Jimenez (OneByJorah)

---

<p align="center">Built with 🌴 by <a href="https://github.com/OneByJorah">OneByJorah</a> · <a href="https://jorahone.com">jorahone.com</a></p>
