#!/usr/bin/env bash
# Author: MilanWoj
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

for name in metrics-writer frontend backend llama-embed llama-gen; do
    echo "stopping $name"
    stop_process "$name"
done

kill_port "$GEN_PORT"
kill_port "$EMBED_PORT"

cd "$PROJECT_ROOT"
docker compose -f infra/docker/docker-compose.yml --profile prod down

echo "stack stopped"