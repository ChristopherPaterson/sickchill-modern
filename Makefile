.PHONY: help backend-install backend-dev backend-test backend-lint frontend-install frontend-dev frontend-build build up

help:
	@echo "Targets:"
	@echo "  backend-install   Create venv and install backend deps (uv)"
	@echo "  backend-dev       Run the API with autoreload on :8080"
	@echo "  backend-test      Run backend tests"
	@echo "  backend-lint      Ruff lint the backend"
	@echo "  frontend-install  Install frontend deps (npm)"
	@echo "  frontend-dev      Run the Vite dev server on :5173"
	@echo "  frontend-build    Build the SPA into backend/static"
	@echo "  build             Build the combined Docker image"
	@echo "  up                docker compose up -d"

backend-install:
	cd backend && uv venv --python 3.12 .venv && uv pip install --python .venv -e ".[dev]"

backend-dev:
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

backend-test:
	cd backend && .venv/bin/pytest -q

backend-lint:
	cd backend && .venv/bin/ruff check app

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

build:
	docker build -f docker/Dockerfile -t sickchill-modern .

up:
	docker compose up -d
