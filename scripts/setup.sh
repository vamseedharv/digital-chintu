#!/usr/bin/env bash
# Bootstraps the backend virtualenv and frontend dependencies.
# Works on Linux, macOS, Raspberry Pi OS, and Git Bash/WSL on Windows.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Backend: creating virtualenv and installing dependencies"
cd "$ROOT_DIR/backend"
# Prefer `python` over `python3`: on some Windows setups `python3` resolves to
# a Microsoft Store stub pointing at a different Python install than `python`,
# which would silently recreate .venv against the wrong interpreter on rerun.
if [ ! -d .venv ]; then
  if command -v python >/dev/null 2>&1; then
    python -m venv .venv
  else
    python3 -m venv .venv
  fi
fi

if [ -f .venv/bin/python ]; then
  VENV_PY=.venv/bin/python
else
  VENV_PY=.venv/Scripts/python.exe
fi

"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -e ".[dev]"
[ -f .env ] || cp .env.example .env

echo "==> Frontend: installing dependencies"
cd "$ROOT_DIR/frontend-dashboard"
npm install
[ -f .env ] || cp .env.example .env

echo "==> Root: preparing .env for docker compose"
cd "$ROOT_DIR"
[ -f .env ] || cp .env.example .env

echo "Setup complete."
