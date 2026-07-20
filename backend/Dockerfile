# python:3.12-slim is multi-arch (amd64/arm64/armv7) — works on Linux, Windows
# (via Docker Desktop), and Raspberry Pi without changes.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml ./

# Install dependencies against a throwaway placeholder package first, so this
# (slow, network-bound) layer only invalidates when pyproject.toml changes —
# not on every application source edit.
RUN mkdir app && touch app/__init__.py \
    && pip install --no-cache-dir . \
    && rm -rf app

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

# Re-install the local package (no network needed, dependencies are already
# in place) so the real application code takes effect.
RUN pip install --no-cache-dir --no-deps .

RUN useradd --create-home --uid 1000 chintu \
    && mkdir -p /app/data /app/logs \
    && chown -R chintu:chintu /app

USER chintu

EXPOSE 8000

# Migrate then serve — a separate step, not baked into app startup code, so
# it runs exactly once per container start regardless of how many workers
# uvicorn spawns (see docs/architecture/03_DATABASE_DESIGN.md).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
