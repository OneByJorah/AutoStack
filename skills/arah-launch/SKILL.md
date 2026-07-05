---
name: arah-launch
description: Launches arah after setup. Use when the stack is configured and ready to start. Use after setup wizard or manual `.env` edits.
---

# arah Launch

## Overview
Bring the stack online in the correct order, verify access from the intended path, and confirm the dashboard is reachable.

## When to Use
- After applying a profile
- After tunnel DNS changes
- After adding new services
- First deployment to a host

## Process

1. **Preflight**
   - Confirm `.env` exists and `STACK_MODE` is set
   - Confirm Docker is running
   - Confirm ports are free: `ss -tlnp | grep -E '8000|6333|8080|8083|8090|9500'`

2. **Launch**
   - Local/tailscale:
     ```bash
     sudo docker compose up -d
     ```
   - Cloudflare/all:
     ```bash
     sudo systemctl enable --now cloudflared || sudo systemctl restart cloudflared
     sudo docker compose up -d
     ```

3. **Verify access**
   - Local: `http://localhost:<port>`
   - Tailscale: `http://<tailscale-ip>:<port>`
   - Cloudflare: `https://arah.<domain>/<path>`

4. **Confirm dashboard**
   - Open NOC UI at the appropriate base URL
   - Confirm services show green

## Rollback
```bash
sudo docker compose down
```

## Boundaries
- Always run `scripts/healthcheck.sh` after launch
- Ask before publishing tunnel DNS to users
- Never launch with `.env` missing or placeholder values
