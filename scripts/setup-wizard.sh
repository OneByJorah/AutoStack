#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== AutoStack setup wizard ==="
echo "Select stack access mode:"
echo "  1) local      (host networking, no tunnels)"
echo "  2) tailscale  (Tailscale-only access)"
echo "  3) cloudflare (Cloudflare Tunnel public HTTPS)"
echo "  4) all        (Tailscale + Cloudflare + local)"

read -rp "Choice [1-4]: " choice
case "$choice" in
  1) MODE=local ;;
  2) MODE=tailscale ;;
  3) MODE=cloudflare ;;
  4) MODE=all ;;
  *) echo "Invalid choice"; exit 1 ;;
esac

PROFILE_DIR="$REPO_ROOT/profiles/$MODE"
if [ ! -f "$PROFILE_DIR/.env" ]; then
  echo "Profile not found: $PROFILE_DIR/.env"
  exit 1
fi

cp "$PROFILE_DIR/.env" "$REPO_ROOT/.env"
echo "Applied profile: $MODE"

# Optional token/secret prompts
read -rp "Enter Honcho API key (leave empty to skip): " HONCHO_KEY
read -rp "Enter OpenRouter / LLM key (leave empty to skip): " LLM_KEY
read -rp "Enter Cloudflare Tunnel hostname (required for cloudflare/all): " CF_HOSTNAME
read -rp "Enter Cloudflare Tunnel name: " CF_TUNNEL

if [ -n "$HONCHO_KEY" ]; then
  mkdir -p "$REPO_ROOT/honcho"
  echo "HONCHO_TOKEN=$HONCHO_KEY" >> "$REPO_ROOT/honcho/.env.honcho"
fi
if [ -n "$LLM_KEY" ]; then
  echo "LLM_API_KEY=$LLM_KEY" >> "$REPO_ROOT/.env"
fi

if [[ "$MODE" == "cloudflare" || "$MODE" == "all" ]]; then
  if [ -z "${CF_HOSTNAME:-}" ]; then
    echo "Cloudflare profile selected but no hostname provided."
    exit 1
  fi
  mkdir -p ~/.cloudflared
  if [ ! -f ~/.cloudflared/config.yml ]; then
    echo "Please run: cloudflared tunnel login && cloudflared tunnel create $CF_TUNNEL"
    echo "Then re-run this wizard."
    exit 1
  fi
  SERVER_IP="${SERVER_IP:-100.66.142.21}"
  cat > ~/.cloudflared/config.yml <<EOF
tunnel: ${CF_TUNNEL}
credentials-file: /home/j1admin/.cloudflared/${CF_TUNNEL}.json
ingress:
  - hostname: ${CF_HOSTNAME}
    path: /honcho/*
    service: http://${SERVER_IP}:8000
  - hostname: ${CF_HOSTNAME}
    path: /qdrant/*
    service: http://${SERVER_IP}:6333
  - hostname: ${CF_HOSTNAME}
    path: /search/*
    service: http://${SERVER_IP}:8080
  - hostname: ${CF_HOSTNAME}
    path: /obsidian/*
    service: http://${SERVER_IP}:8083
  - hostname: ${CF_HOSTNAME}
    path: /costforge/*
    service: http://${SERVER_IP}:8090
  - hostname: ${CF_HOSTNAME}
    path: /noc/*
    service: http://${SERVER_IP}:9500
  - service: http_status:404
EOF
  sudo systemctl enable --now cloudflared || true
fi

echo "Restarting stack..."
cd "$REPO_ROOT"
sudo docker compose up -d

echo "Running healthcheck..."
bash "$REPO_ROOT/scripts/healthcheck.sh" || true

echo "Done. Profile: $MODE"
