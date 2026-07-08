# Setup Wizard

AutoStack supports four access modes. Choose one at install time, or switch later by updating `.env`.

- `local` — no tunnels, no tailscale, no cloudflare; services reachable on localhost ports only.
- `tailscale` — services exposed over Tailscale only.
- `cloudflare` — one public HTTPS hostname using a Cloudflare Tunnel.
- `all` — local + Tailscale + Cloudflare.

Methods:
1. **CLI wizard**
2. **Web setup** (optional)

## CLI wizard
```bash
bash scripts/setup-wizard.sh
```
Prompts for mode, Cloudflare tunnel details, and optional API keys. Writes `.env`, configures Cloudflare if requested, brings the stack up, and runs the healthcheck.

## Web setup
Enable the dashboard setup API:
```bash
ENABLE_SETUP_API=1 docker compose -f docker-compose.yml -f noc-dashboard/docker-compose.dashboard.yml up -d
```

Then open:
- `http://localhost:9500/setup`
- Or, if the Cloudflare tunnel is active: `https://autostack.<your-domain>.com/setup`

Select mode, enter tokens/tunnel info, and submit.

What happens next:
- The backend writes `.env`, optional `setup-complete.json`, and the Cloudflare tunnel config if requested.
- If the host `scripts/apply-setup.sh` can be triggered from the container, it runs automatically.
- Otherwise, the response includes the exact command to finish the setup from the host:
  ```bash
  bash scripts/apply-setup.sh
  ```

## Host-side apply script
```bash
bash scripts/apply-setup.sh
```
Reads `setup-complete.json`, applies the chosen profile, writes the Cloudflare tunnel config, restarts Cloudflare Tunnel and the Docker stack, and runs the healthcheck.

## Profiles
| Profile | File |
|---------|------|
| local | `profiles/local/.env` |
| tailscale | `profiles/tailscale/.env` |
| cloudflare | `profiles/cloudflare/.env` |
| all | `profiles/all/.env` |

## Verify
```bash
bash scripts/healthcheck.sh
```
