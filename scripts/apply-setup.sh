#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SETUP_STATE="${SETUP_STATE:-$REPO_ROOT/setup-complete.json}"
cf_config="${cf_config:-$HOME/.cloudflared/config.yml}"

if [ ! -f "$SETUP_STATE" ]; then
  echo "No setup state found at $SETUP_STATE"
  exit 1
fi

mode=$(python3 -c "import json; print(json.load(open('$SETUP_STATE'))['mode'])")
if [ -z "${mode:-}" ]; then
  echo "Invalid setup state"
  exit 1
fi

profile="$REPO_ROOT/profiles/$mode/.env"
if [ -f "$profile" ]; then
  cp "$profile" "$REPO_ROOT/.env"
  echo "Applied profile .env from $profile"
else
  echo "Profile missing: $profile"
  exit 1
fi

cf_host=$(python3 -c "import json; print(json.load(open('$SETUP_STATE')).get('cloudflare_hostname',''))")
cf_tunnel=$(python3 -c "import json; print(json.load(open('$SETUP_STATE')).get('cloudflare_tunnel',''))")

if [[ "$mode" == "cloudflare" || "$mode" == "all" ]]; then
  if [ -n "$cf_host" ] && [ -n "$cf_tunnel" ]; then
    mkdir -p "$(dirname "$cf_config")"
    cat > "$cf_config" <<EOF
tunnel: ${cf_tunnel}
credentials-file: /home/j1admin/.cloudflared/${cf_tunnel}.json
ingress:
  - hostname: ${cf_host}
    path: /honcho/*
    service: http://<tailscale-ip>:8000
  - hostname: ${cf_host}
    path: /qdrant/*
    service: http://<tailscale-ip>:6333
  - hostname: ${cf_host}
    path: /search/*
    service: http://<tailscale-ip>:8080
  - hostname: ${cf_host}
    path: /obsidian/*
    service: http://<tailscale-ip>:8083
  - hostname: ${cf_host}
    path: /costforge/*
    service: http://<tailscale-ip>:8090
  - hostname: ${cf_host}
    path: /noc/*
    service: http://<tailscale-ip>:9500
  - service: http_status:404
EOF
    echo "Wrote Cloudflare tunnel config to $cf_config"
    sudo systemctl enable --now cloudflared || true
    sudo systemctl restart cloudflared || true
  else
    echo "Cloudflare mode selected but hostname/tunnel missing; skipping tunnel write"
  fi
else
  echo "Mode=$mode: skipping Cloudflare setup"
fi

echo "Restarting Docker stack..."
sudo docker compose up -d

echo "Running healthcheck..."
bash "$REPO_ROOT/scripts/healthcheck.sh" || true

echo "arah setup applied: mode=$mode"
