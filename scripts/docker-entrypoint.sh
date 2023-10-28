#! /usr/bin/env bash

alembic upgrade head
cd /code/shop_api
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
gunicorn -k uvicorn.workers.UvicornWorker -w 1 --bind 0.0.0.0:8080 --bind 0.0.0.0:8080