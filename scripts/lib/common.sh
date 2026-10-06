#!/usr/bin/env bash
# Author: MilanWoj
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"
mkdir -p "$PID_DIR"

GEN_PORT=8080
EMBED_PORT=8081
BACKEND_PORT=8000
FRONTEND_PORT=5173
QDRANT_PORT=6333
SEARXNG_PORT=8888

GEN_MODEL="bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M"
EMBED_MODEL="nomic-ai/nomic-embed-text-v1.5-GGUF:Q8_0"

wait_for_url() {
    local url="$1"
    local timeout="${2:-60}"
    local elapsed=0
    while ! curl -sf "$url" >/dev/null 2>&1; do
        sleep 1
        elapsed=$((elapsed + 1))
        if [ "$elapsed" -ge "$timeout" ]; then
            echo "timed out waiting for $url" >&2
            return 1
        fi
    done
}

start_background() {
    local name="$1"
    shift
    "$@" >"$PROJECT_ROOT/.logs/$name.log" 2>&1 &
    echo $! > "$PID_DIR/$name.pid"
}

stop_process() {
    local name="$1"
    local pid_file="$PID_DIR/$name.pid"
    if [ ! -f "$pid_file" ]; then
        echo "$name: no pid file, skipping"
        return 0
    fi

    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
        for _ in $(seq 1 10); do
            kill -0 "$pid" 2>/dev/null || break
            sleep 0.5
        done
        kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
}

kill_port() {
    local port="$1"
    local pids
    pids=$(lsof -ti "tcp:$port" 2>/dev/null || true)
    [ -z "$pids" ] && return 0

    echo "port $port still held by pid(s) $pids, killing"
    kill $pids 2>/dev/null || true
    sleep 1
    pids=$(lsof -ti "tcp:$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        kill -9 $pids 2>/dev/null || true
    fi
    return 0
}

mkdir -p "$PROJECT_ROOT/.logs"