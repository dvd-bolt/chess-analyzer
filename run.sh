#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN=".venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 не найден. Установи Python 3.10+ и запусти снова."
    exit 1
  fi

  python3 -m venv .venv
fi

if ! "$PYTHON_BIN" -c "import fastapi, uvicorn, chess" >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install -r requirements.txt
fi

exec "$PYTHON_BIN" -m uvicorn main:app --reload --host 127.0.0.1 --port "${PORT:-8000}"
