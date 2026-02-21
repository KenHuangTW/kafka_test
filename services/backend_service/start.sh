#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="${PYTHONPATH:-.}"
export KAFKA_GROUP_ID="${KAFKA_GROUP_ID:-backend-group}"
export KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8003}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-microservices-kafka}"
RELOAD="${RELOAD:-1}"

UVICORN_ARGS=(services.backend_service.app.main:app --host "$HOST" --port "$PORT")
if [[ "$RELOAD" == "1" ]]; then
  UVICORN_ARGS+=(--reload)
fi

if command -v uvicorn >/dev/null 2>&1; then
  exec uvicorn "${UVICORN_ARGS[@]}"
fi

if command -v conda >/dev/null 2>&1; then
  exec conda run --no-capture-output -n "$CONDA_ENV_NAME" \
    python -m uvicorn "${UVICORN_ARGS[@]}"
fi

echo "Error: uvicorn not found and conda is unavailable." >&2
exit 1
