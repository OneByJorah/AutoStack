#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ ! -f "${REPO_DIR}/.env.headroom" ]; then
  cp "${REPO_DIR}/.env.headroom.example" "${REPO_DIR}/.env.headroom"
  echo "Created .env.headroom from example."
fi

echo "Headroom init complete."
echo "Edit .env.headroom (proxy settings)."
echo "NOTE: NEO4J_AUTH is interpolated by docker-compose.headroom.yml from the root .env —"
echo "      add 'NEO4J_AUTH=neo4j/<password>' there before first start."
echo "Start: docker compose -f docker-compose.yml -f docker-compose.headroom.yml up -d"
