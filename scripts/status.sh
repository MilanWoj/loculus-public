#!/usr/bin/env bash
# Author: MilanWoj
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

check() {
    local label="$1"
    local url="$2"
    if curl -sf "$url" >/dev/null 2>&1; then
        echo "  $label: up"
    else
        echo "  $label: down"
    fi
}

echo "services:"
check "generation LLM" "http://127.0.0.1:$GEN_PORT/health"
check "embeddings"     "http://127.0.0.1:$EMBED_PORT/health"
check "qdrant"         "http://127.0.0.1:$QDRANT_PORT/collections"
check "searxng"        "http://127.0.0.1:$SEARXNG_PORT/"
check "backend"        "http://127.0.0.1:$BACKEND_PORT/api/health"

echo ""
echo "memory:"
ps -o rss=,command= -p "$(cat "$PID_DIR/llama-gen.pid" 2>/dev/null)" 2>/dev/null | awk '{printf "  generation LLM: %.0f MB\n", $1/1024}'
ps -o rss=,command= -p "$(cat "$PID_DIR/llama-embed.pid" 2>/dev/null)" 2>/dev/null | awk '{printf "  embeddings: %.0f MB\n", $1/1024}'
docker stats loculus-qdrant loculus-searxng --no-stream --format '  {{.Name}}: {{.MemUsage}}' 2>/dev/null
