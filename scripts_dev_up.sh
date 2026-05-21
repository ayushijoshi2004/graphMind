#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q fastapi uvicorn pandas plotly pydantic requests python-multipart

echo "Starting backend on http://127.0.0.1:8000"
uvicorn backend.app:app --reload &
BACK_PID=$!

cleanup() {
  kill "$BACK_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cd frontend
if [ ! -d node_modules ]; then
  npm install
fi

echo "Starting frontend on http://127.0.0.1:5173"
npm run dev
