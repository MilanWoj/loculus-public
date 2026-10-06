#!/usr/bin/env bash
# Author: MilanWoj
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

echo "starting generation model on port $GEN_PORT"
start_background llama-gen llama-server -hf "$GEN_MODEL" --offline --port "$GEN_PORT" --ctx-size 4096

echo "starting embedding model on port $EMBED_PORT"
start_background llama-embed llama-server -hf "$EMBED_MODEL" --offline --port "$EMBED_PORT" --ctx-size 2048 --embedding

wait_for_url "http://127.0.0.1:$GEN_PORT/health" 120
wait_for_url "http://127.0.0.1:$EMBED_PORT/health" 120

echo "starting containers"
cd "$PROJECT_ROOT"
docker compose -f infra/docker/docker-compose.yml --profile prod up -d

wait_for_url "http://127.0.0.1:$QDRANT_PORT/collections" 60
wait_for_url "http://127.0.0.1:$BACKEND_PORT/api/health" 60

echo "starting metrics collector"
start_background metrics-writer bash "$SCRIPT_DIR/lib/metrics_writer.sh"

echo "stack is up"
