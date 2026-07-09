# Requires a POSIX shell (Linux, macOS, Raspberry Pi OS, or Git Bash/WSL on
# Windows). On native Windows without `make`, use scripts/setup.ps1 and run
# the equivalent commands directly — see backend/README.md and
# frontend-dashboard/README.md.

# Detect by which interpreter actually exists (not by host OS name): a .venv
# created inside WSL/Linux and used from native Windows, or vice versa, would
# otherwise compute a path that doesn't exist.
ifneq ($(wildcard backend/.venv/bin/python),)
	VENV_PY := .venv/bin/python
else
	VENV_PY := .venv/Scripts/python.exe
endif

.PHONY: setup backend-dev frontend-dev lint format test docker-up docker-down

setup:
	bash scripts/setup.sh

backend-dev:
	cd backend && $(VENV_PY) -m uvicorn app.main:app --reload

frontend-dev:
	cd frontend-dashboard && npm run dev

lint:
	cd backend && $(VENV_PY) -m ruff check . && $(VENV_PY) -m mypy .
	cd frontend-dashboard && npm run lint && npm run typecheck

format:
	cd backend && $(VENV_PY) -m black .
	cd frontend-dashboard && npm run format

test:
	cd backend && $(VENV_PY) -m pytest
	cd frontend-dashboard && npm run test

docker-up:
	docker compose up --build

docker-down:
	docker compose down
