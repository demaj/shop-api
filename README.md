# Shop API

FastAPI + async SQLAlchemy shop backend. All API routes live under `/api/v1`;
interactive docs at [http://localhost:8080/docs](http://localhost:8080/docs).

## Getting started

### Requirements

- docker
- docker compose

### Environment

Copy the sample env file and fill in real values before the first start:

```bash
cp .envs/.local/app.sample.env .envs/.local/app.secrets.env
```

- `SECRET_KEY` must be at least 32 characters — generate one with `openssl rand -hex 32`
- `FIRST_SUPERUSER_PASSWORD` must be at least 8 characters
- `DATABASE_URI` must use the async driver prefix: `postgresql+asyncpg://...`

### Startup

```bash
make start
make migrate
```

The first superuser (from `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`) is created
automatically on application startup.

### Run tests

```bash
make test          # inside the web container (needs the db service running)
make lint          # ruff check + ruff format --check
make format        # ruff auto-fix + format
```

### Dependencies

Dependencies are managed with [uv](https://docs.astral.sh/uv/): runtime deps live in
`pyproject.toml` `[project.dependencies]`, dev tools in `[dependency-groups] dev`, and
exact versions are pinned in `uv.lock`. After changing a dependency, run `make lock` (or
`uv lock`) and rebuild. To work locally without Docker: `uv sync` then `uv run pytest`.

## Authentication

Write endpoints (POST/PUT/DELETE) require a bearer token; reads are public.

```bash
# 1. Get a token (the OAuth2 form field is `username`, but it carries the email)
curl -X POST http://localhost:8080/api/v1/auth/token \
  -d 'username=<FIRST_SUPERUSER>&password=<FIRST_SUPERUSER_PASSWORD>'

# 2. Use it
curl -X POST http://localhost:8080/api/v1/categories \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Tea"}'
```

`GET /api/v1/users/me` returns the authenticated user; `POST /api/v1/users` creates
users (superusers only). Prices are integers in **cents**.

## Production

Production is a self-contained compose file. Fill in both secret files, then run it
from the repo root so relative paths resolve correctly:

```bash
cp .envs/.production/app.sample.env .envs/.production/app.secrets.env  # SECRET_KEY, superuser, DATABASE_URI
cp .envs/.production/db.sample.env  .envs/.production/db.secrets.env   # POSTGRES_* (must match DATABASE_URI)
docker compose --project-directory . -f docker/production.yml up -d --build
```

The production entrypoint applies migrations and serves with multiple uvicorn workers
(`WEB_CONCURRENCY`, default 2). Postgres is not published to the host, and the database
container never receives the application's `SECRET_KEY` or superuser password.

### To-Do

- Docs
- Redis
- Traefik
- Celery
- dbdiagram.io
- Host Render
