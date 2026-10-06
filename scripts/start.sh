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

echo "starting Qdrant and SearXNG"
cd "$PROJECT_ROOT"
docker compose -f infra/docker/docker-compose.yml up -d qdrant searxng

wait_for_url "http://127.0.0.1:$QDRANT_PORT/collections" 60

echo "starting backend"
cd "$PROJECT_ROOT/backend"
start_background backend uv run uvicorn app.main:app --reload --port "$BACKEND_PORT"

wait_for_url "http://127.0.0.1:$BACKEND_PORT/api/health" 60

echo "starting frontend"
cd "$PROJECT_ROOT/frontend"
start_background frontend npm run dev

echo "starting metrics collector"
start_background metrics-writer bash "$SCRIPT_DIR/lib/metrics_writer.sh"

echo "dev stack is up: http://127.0.0.1:$FRONTEND_PORT"
