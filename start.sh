#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

services=(
  "main:services/main_service/start.sh"
  "payment:services/payment_service/start.sh"
  "backend:services/backend_service/start.sh"
)

declare -a pids=()

cleanup() {
  for pid in "${pids[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}

trap cleanup INT TERM EXIT

for service in "${services[@]}"; do
  name="${service%%:*}"
  script="${service#*:}"
  echo "Starting ${name} service..."
  bash "$script" &
  pids+=("$!")
done

wait "${pids[@]}"
