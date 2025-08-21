#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Usage: scripts/run_all.sh <start|stop|status|test>
# This script launches the backend (venv + uvicorn) and frontend (npm start) in background.
# It stores PIDs in $ROOT/.pids_run_all and logs in $ROOT/logs/

CMD="${1:-start}"
VENV=".venv"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"
FRONTEND_DIR="$ROOT/frontend"
PIDS_FILE="$ROOT/.pids_run_all"
LOG_DIR="$ROOT/logs"

has_cmd() { command -v "$1" >/dev/null 2>&1; }

ensure_dirs() {
  mkdir -p "$LOG_DIR"
}

ensure_venv() {
  if [ ! -d "$VENV" ]; then
    echo "Creating venv at $VENV"
    python3 -m venv "$VENV"
    "$PIP" install -U pip
    echo "Installing backend dependencies..."
    "$PIP" install -r backend/requirements.txt || true
  fi
}

start_backend() {
  ensure_venv
  export DATABASE_URL="${DATABASE_URL:-sqlite:///./backend/dev.db}"
  echo "Starting backend (uvicorn) with DATABASE_URL=$DATABASE_URL"
  nohup "$PY" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
  echo $! > "$PIDS_FILE.backend"
  echo "Backend PID: $(cat $PIDS_FILE.backend) -> logs at $LOG_DIR/backend.log"
}

start_frontend() {
  if ! has_cmd npm; then
    echo "npm not found in PATH; please install Node.js and npm to run the frontend." >&2
    return 1
  fi
  echo "Starting frontend (npm start) in $FRONTEND_DIR"
  cd "$FRONTEND_DIR"
  if [ ! -d node_modules ]; then
    echo "Installing frontend dependencies (npm install)..."
    npm install || true
  fi
  nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
  echo $! > "$PIDS_FILE.frontend"
  echo "Frontend PID: $(cat $PIDS_FILE.frontend) -> logs at $LOG_DIR/frontend.log"
  cd "$ROOT"
}

stop_all() {
  echo "Stopping processes listed in $PIDS_FILE"
  for f in "$PIDS_FILE".* "$PIDS_FILE".* ; do :; done 2>/dev/null || true
  # stop backend
  if [ -f "$PIDS_FILE.backend" ]; then
    pid=$(cat "$PIDS_FILE.backend")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" && echo "Stopped backend ($pid)" || true
    fi
    rm -f "$PIDS_FILE.backend"
  fi
  # stop frontend
  if [ -f "$PIDS_FILE.frontend" ]; then
    pid=$(cat "$PIDS_FILE.frontend")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" && echo "Stopped frontend ($pid)" || true
    fi
    rm -f "$PIDS_FILE.frontend"
  fi
}

status_all() {
  echo "Status:"
  if [ -f "$PIDS_FILE.backend" ]; then
    pid=$(cat "$PIDS_FILE.backend")
    if kill -0 "$pid" 2>/dev/null; then
      echo " backend: running (pid $pid)"
    else
      echo " backend: not running (stale pid $pid)"
    fi
  else
    echo " backend: not running"
  fi

  if [ -f "$PIDS_FILE.frontend" ]; then
    pid=$(cat "$PIDS_FILE.frontend")
    if kill -0 "$pid" 2>/dev/null; then
      echo " frontend: running (pid $pid)"
    else
      echo " frontend: not running (stale pid $pid)"
    fi
  else
    echo " frontend: not running"
  fi
}

run_tests() {
  ensure_venv
  echo "Running backend tests"
  "$PY" -m pytest backend/tests -xvs
}

case "$CMD" in
  start)
    ensure_dirs
    start_backend || true
    # attempt frontend but don't fail script if it can't start
    (start_frontend) || echo "frontend not started"
    ;;
  stop)
    stop_all
    ;;
  status)
    status_all
    ;;
  test)
    run_tests
    ;;
  *)
    echo "Usage: $0 {start|stop|status|test}"
    exit 1
    ;;
esac
