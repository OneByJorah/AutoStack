# arah setup wizard

## Modes
- `local`: no tunnels, no tailscale, no cloudflare; services reachable on localhost ports only
- `tailscale`: services exposed over Tailscale only
- `cloudflare`: one public HTTPS hostname using a Cloudflare Tunnel
- `all`: local + Tailscale + Cloudflare

## CLI wizard
```bash
bash scripts/setup-wizard.sh
```
It asks for the mode, then prompts for Cloudflare details and optional API keys.

## Web setup (opt-in)
Set `ENABLE_SETUP_API=1` in `noc-dashboard/docker-compose.dashboard.yml`, then open:
- `http://localhost:9500/setup`
- Select mode, enter tokens and tunnel info, submit.

## Profiles
- `profiles/local/.env`
- `profiles/tailscale/.env`
- `profiles/cloudflare/.env`
- `profiles/all/.env`

## After applying
- `.env` is updated
- Cloudflare tunnel config is written if requested
- `docker compose up -d` restarts the stack
- healthchecks run and print status
