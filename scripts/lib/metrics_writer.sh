#!/usr/bin/env bash
# Author: MilanWoj
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
set +e

mkdir -p "$PROJECT_ROOT/infra/run"
OUT_FILE="$PROJECT_ROOT/infra/run/host-metrics.json"

while true; do
    gen_ram=$(ps -o rss= -p "$(cat "$PID_DIR/llama-gen.pid" 2>/dev/null)" 2>/dev/null | awk '{print $1/1024}')
    embed_ram=$(ps -o rss= -p "$(cat "$PID_DIR/llama-embed.pid" 2>/dev/null)" 2>/dev/null | awk '{print $1/1024}')

    qdrant_ram=$(docker stats loculus-qdrant --no-stream --format '{{.MemUsage}}' 2>/dev/null | awk -F'/' '{print $1}')
    searxng_ram=$(docker stats loculus-searxng --no-stream --format '{{.MemUsage}}' 2>/dev/null | awk -F'/' '{print $1}')

    tmp_file="$OUT_FILE.tmp"
    cat > "$tmp_file" <<EOF
{
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "llama_server_ram_mb": ${gen_ram:-null},
  "embedding_server_ram_mb": ${embed_ram:-null},
  "qdrant_ram": "${qdrant_ram:-unknown}",
  "searxng_ram": "${searxng_ram:-unknown}"
}
EOF
    mv "$tmp_file" "$OUT_FILE"
    sleep 5
done
