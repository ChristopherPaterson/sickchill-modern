# One-shot image: builds the Vue frontend, then the FastAPI backend, and serves
# both from a single non-root container. Build context is the repo root:
#   docker build -f docker/Dockerfile -t sickchill-modern .

# Stage 1: build the frontend (outputs to /build/backend/static via vite config)
FROM node:22-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# Stage 2: build a Python venv with the backend installed
FROM python:3.12-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir .

# Stage 3: runtime
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PATH="/venv/bin:$PATH" SCM_DATA_DIR=/data
RUN useradd --create-home --uid 1000 app && mkdir -p /data && chown app /data
WORKDIR /app
COPY --from=builder /venv /venv
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./
COPY --from=frontend /build/backend/static ./static
USER app
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import httpx,sys; sys.exit(0 if httpx.get('http://localhost:8080/healthz').status_code==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
