#! /usr/bin/env bash

alembic upgrade head
cd /code/shop_api
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
