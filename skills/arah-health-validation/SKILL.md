---
name: arah-health-validation
description: Validates arah services with health checks. Use after deploy, restart, config change, or tunnel update. Use when verifying mode switches or troubleshooting.
---

# arah Health Validation

## Overview
Every change to arah must be followed by validation. Use `scripts/healthcheck.sh` and curl checks for each service.

## When to Use
- After `docker compose up -d`
- After `.env` or profile changes
- After tunnel config changes
- When NOC dashboard shows services down

## Process

1. **Run the project healthcheck**
   ```bash
   bash scripts/healthcheck.sh
   ```

2. **Validate by access mode**
   - `local`:
     - `curl -sf http://localhost:8000/healthz` (Honcho)
     - `curl -sf http://localhost:6333/readyz` (Qdrant)
     - `curl -sf http://localhost:8080/search?q=healthcheck&format=json` (SearXNG)
     - `curl -sf http://localhost:8083/` (Obsidian)
   - `tailscale`:
     - `curl -sf http://<tailscale-ip>:<port>/...`
   - `cloudflare` / `all`:
     - `curl -k https://arah.<domain>/honcho/healthz`
     - `curl -k https://arah.<domain>/qdrant/readyz`
     - verify tunnel: `systemctl status cloudflared`

3. **NOC dashboard status API**
   ```bash
   curl -sf http://localhost:9500/api/status | jq '.services'
   ```

4. **Failure checklist**
   - Service image pull failure → disk space / network
   - Port conflict → `ss -tlnp | grep <port>`
   - Tunnel 404 → path mismatch in `~/.cloudflared/config.yml`
   - DB connection failure → PostgreSQL health / credentials

## Success Criteria
- `scripts/healthcheck.sh` exits 0
- All `http` services return `< 500`
- NOC dashboard shows green or graceful warning
