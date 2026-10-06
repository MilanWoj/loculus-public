#!/usr/bin/env bash
# Author: MilanWoj
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

cd "$PROJECT_ROOT"
docker compose -f infra/docker/docker-compose.yml --profile prod build backend

echo "backend image rebuilt"
