#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Usage: scripts/run_backend.sh <start|stop|test|shell|logs>
# Optional: export USE_DOCKER=1 to force docker mode, USE_DOCKER=0 to force venv mode

CMD="${1:-start}"
USE_DOCKER="${USE_DOCKER:-auto}"

has_cmd() { command -v "$1" >/dev/null 2>&1; }

# Decide docker availability
if [ "$USE_DOCKER" = "auto" ]; then
  if has_cmd docker && (has_cmd docker-compose || docker compose version >/dev/null 2>&1); then
    DOCKER_AVAILABLE=1
  else
    DOCKER_AVAILABLE=0
  fi
else
  if [ "$USE_DOCKER" = "1" ] || [ "$USE_DOCKER" = "true" ]; then DOCKER_AVAILABLE=1; else DOCKER_AVAILABLE=0; fi
fi

if [ "$DOCKER_AVAILABLE" -eq 1 ]; then
  if has_cmd docker-compose; then DC="docker-compose"; else DC="docker compose"; fi

  case "$CMD" in
    start)
      echo "Starting services with: $DC up -d"
      $DC up -d
      ;;
    stop)
      echo "Stopping services with: $DC down"
      $DC down
      ;;
    test)
      echo "Running tests inside backend container"
      $DC exec backend pytest -xvs
      ;;
    shell)
      echo "Opening shell in backend container"
      $DC exec backend /bin/sh
      ;;
    logs)
      echo "Tailing logs"
      $DC logs -f
      ;;
    *)
      echo "Usage: $0 {start|stop|test|shell|logs}"
      exit 1
      ;;
  esac
else
  VENV=".venv"
  PY="$VENV/bin/python"
  PIP="$VENV/bin/pip"

  ensure_venv() {
    if [ ! -d "$VENV" ]; then
      echo "Creating venv at $VENV"
      python3 -m venv "$VENV"
      "$PIP" install -U pip
      echo "Installing backend dependencies..."
      "$PIP" install -r backend/requirements.txt || true
    fi
  }

  case "$CMD" in
    start)
      ensure_venv
      export DATABASE_URL="${DATABASE_URL:-sqlite:///./backend/dev.db}"
      echo "Starting uvicorn (host=127.0.0.1 port=8000) with DATABASE_URL=$DATABASE_URL"
      exec "$PY" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
      ;;
    test)
      ensure_venv
      echo "Running pytest locally"
      exec "$PY" -m pytest backend/tests -xvs
      ;;
    shell)
      ensure_venv
      echo "Activating shell with venv (you'll still be in your normal shell; run 'source .venv/bin/activate' to fully activate)"
      exec "$SHELL"
      ;;
    *)
      echo "Usage: $0 {start|test|shell}"
      exit 1
      ;;
  esac
fi
