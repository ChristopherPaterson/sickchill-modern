# Multi-stage build for the SickChill Modern backend.
# Fixes SickChill's Docker issues: current base image, non-root user, no pipe-to-shell.

FROM python:3.12-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN pip install --no-cache-dir build hatchling
COPY pyproject.toml ./
COPY app ./app
# Install into a venv we can copy to the runtime stage.
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir .

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PATH="/venv/bin:$PATH"
# Create a non-root user (SickChill ran as root).
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=builder /venv /venv
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
# Optional: built frontend mounted/copied to ./static is served by FastAPI.
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import httpx,sys; sys.exit(0 if httpx.get('http://localhost:8080/healthz').status_code==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
