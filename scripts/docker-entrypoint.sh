#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head

cd /code/shop_api
# exec: uvicorn becomes PID 1 so container signals reach the server.
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8080}" \
  --workers "${WEB_CONCURRENCY:-2}"
