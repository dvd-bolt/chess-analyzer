#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if ! python -c "import fastapi, uvicorn, chess" >/dev/null 2>&1; then
  python -m pip install -r requirements.txt
fi

python -m uvicorn main:app --reload --host 127.0.0.1 --port "${PORT:-8000}"
