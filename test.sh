#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="${PYTHONPATH:-.}"

pytest -q \
  services/main_service/test \
  services/payment_service/test \
  services/backend_service/test
