#!/bin/sh
set -e

# Render/Railway provide PORT; local Docker defaults to 8000
PORT="${PORT:-8000}"

# Normalize Postgres URLs from managed providers (postgresql:// → driver-specific)
if [ -n "$DATABASE_URL" ]; then
  case "$DATABASE_URL" in
    postgres://*) export DATABASE_URL="$(echo "$DATABASE_URL" | sed 's|^postgres://|postgresql+asyncpg://|')" ;;
    postgresql://*) export DATABASE_URL="$(echo "$DATABASE_URL" | sed 's|^postgresql://|postgresql+asyncpg://|')" ;;
  esac
fi

if [ -n "$DATABASE_URL_SYNC" ]; then
  case "$DATABASE_URL_SYNC" in
    postgres://*) export DATABASE_URL_SYNC="$(echo "$DATABASE_URL_SYNC" | sed 's|^postgres://|postgresql+psycopg2://|')" ;;
    postgresql://*) export DATABASE_URL_SYNC="$(echo "$DATABASE_URL_SYNC" | sed 's|^postgresql://|postgresql+psycopg2://|')" ;;
  esac
fi

echo "Running database migrations..."
alembic upgrade head

if [ "$AUTO_SEED" = "true" ]; then
  echo "Seeding database (AUTO_SEED=true)..."
  python -m scripts.seed || true
fi

echo "Starting API on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
