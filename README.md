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

The API is served on `http://localhost:8080` through the same HAProxy configuration as
production (see "Reverse proxy"), so local requests get the same limits and headers. Two things
differ locally: there is no TLS, and the failed-login limit is raised to 1000 per minute. To try
the real limit, start with `LOGIN_FAILURE_LIMIT=5 make start`. The application is also reachable
directly, bypassing the proxy, on `http://127.0.0.1:8081`.

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

## Errors

Every error is an [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) problem document, served as
`application/problem+json`:

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Product 3f2a8c1e-... not found",
  "code": "resource_not_found",
  "request_id": "9b1c0d5e-..."
}
```

- Branch on `code`. It is stable; `detail` and `title` are for humans and may be reworded.
- `request_id` equals the `X-Request-Id` response header. Quote it when reporting a problem.
- A `422` from request validation adds `errors`, one item per invalid field: `pointer` (a JSON
  Pointer into the body) or `parameter` (a query or path parameter), plus `code` and `detail`.
  Malformed JSON gives one item with neither. Other `422` responses have no `errors`.

| Status | `code` | Meaning |
| --- | --- | --- |
| 400 | `bad_request` | The request is malformed |
| 401 | `unauthenticated` | Missing, invalid or expired token |
| 401 | `invalid_credentials` | Login failed |
| 403 | `forbidden` | The account lacks the required privileges |
| 403 | `account_inactive` | The account is deactivated |
| 404 | `route_not_found` | No such path |
| 404 | `resource_not_found` | The category or product does not exist |
| 405 | `method_not_allowed` | The path exists but not for this method (see `Allow`) |
| 409 | `already_exists` | A resource with these unique values already exists |
| 409 | `reference_not_found` | A referenced resource (for example `category_id`) does not exist |
| 409 | `resource_in_use` | The resource cannot be deleted while others reference it |
| 413 | `payload_too_large` | The request body is larger than 1 MiB |
| 422 | `validation_failed` | The request did not pass validation |
| 429 | `rate_limited` | Too many failed login attempts from this address; see `Retry-After` |
| 500 | `internal_error` | Unexpected server error |
| 503 | `service_unavailable` | A dependency is temporarily unavailable |

Retrying: a `429` or a `503` with a `Retry-After` header is safe to retry after that many seconds. A `503`
without one means the request timed out; back off before retrying. Do not retry `4xx` responses
unchanged, and do not retry a `500` on a write without checking whether it took effect.

## Production

Production is a self-contained compose file. Fill in both secret files, then run it
from the repo root so relative paths resolve correctly:

```bash
cp .envs/.production/app.sample.env .envs/.production/app.secrets.env  # SECRET_KEY, superuser, DATABASE_URI
cp .envs/.production/db.sample.env  .envs/.production/db.secrets.env   # POSTGRES_* (must match DATABASE_URI)
docker compose --project-directory . -f docker/production.yml up -d --build
```

The production entrypoint applies migrations and serves with multiple uvicorn workers
(`WEB_CONCURRENCY`, default 2). Neither the application nor Postgres is published to the host,
and the database container never receives the application's `SECRET_KEY` or superuser password.

Password hashing is the memory-heavy part of the service: each verification uses about 64 MiB.
`PASSWORD_HASH_CONCURRENCY` (default 4) caps how many run at once in each worker, and the `web`
container is limited to `WEB_MEMORY_LIMIT` (default `1g`). If you raise `WEB_CONCURRENCY` or the
hashing cap, raise the limit too: allow roughly 300 MiB plus workers x cap x 64 MiB.

### Reverse proxy

All traffic enters through HAProxy (`docker/haproxy/haproxy.cfg`); the application container is
not published to the host. The proxy:

- limits failed logins: after 5 failed attempts within a minute from one address, further logins
  from that address get `429` with `Retry-After: 60`, including ones with the right password
  (`LOGIN_FAILURE_LIMIT` changes the 5);
- rejects request bodies over 1 MiB with `413`;
- adds `X-Content-Type-Options`, `Referrer-Policy` and `X-Frame-Options`, and assigns the
  `X-Request-Id` when the client did not send one;
- answers `503` in the same error format while the application is starting or down.

By default it listens on `127.0.0.1:8080` over plain HTTP, which is only suitable for local use
or behind another TLS terminator. Do not publish it on a public address without TLS: logins would
send passwords in clear text.

To switch TLS on, once a domain name points at the server:

1. Put the certificate and its private key, concatenated into one `.pem` file, in the
   `proxy_certs` volume (mounted at `/etc/haproxy/certs` in the proxy).
2. Start the stack with `TLS_DOMAIN=<your domain>`, `PROXY_HTTP_BIND=0.0.0.0:80` and
   `PROXY_HTTPS_BIND=0.0.0.0:443` in the environment of the `docker compose` command.

With `TLS_DOMAIN` set, the proxy serves HTTPS, redirects HTTP to it, sends
`Strict-Transport-Security`, and refuses requests for any other host name. Obtaining and renewing
the certificate is not automated yet.

### To-Do

- Docs
- Redis
- Traefik
- Celery
- dbdiagram.io
- Host Render
- OAuth/OIDC and JWT-based authentication
- OpenTelemetry
