#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://127.0.0.1:5173"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is not installed. Install uv first, then rerun this script."
  exit 1
fi

if ! command -v bun >/dev/null 2>&1; then
  echo "Error: bun is not installed. Install bun first, then rerun this script."
  exit 1
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

cd "$ROOT_DIR"
echo "[1/4] Sync Python dependencies"
uv sync

echo "[2/4] Install frontend dependencies"
(cd frontend && bun install)

echo "[3/4] Start backend: $BACKEND_URL"
uv run python -m uvicorn app.main:app --port 8000 --reload --app-dir backend &
BACKEND_PID=$!

echo "[4/4] Start frontend: $FRONTEND_URL"
(cd frontend && bun run dev --host 127.0.0.1 --port 5173 --strictPort) &
FRONTEND_PID=$!

echo
echo "Cranfield IR is starting."
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL/api/health"
echo "Press Ctrl+C to stop both services."
echo

wait "$BACKEND_PID" "$FRONTEND_PID"
