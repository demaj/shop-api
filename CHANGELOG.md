# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

History before this file was started (2021 to 2025) is available in the git log only.

## [Unreleased]

### Added

- Authentication: `POST /api/v1/auth/token` issues a JWT access token (OAuth2 password flow, the
  username is the email), and `GET /api/v1/users/me` returns the current user.
- `POST /api/v1/users` to create users, restricted to superusers.
- The first superuser is created on startup from `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD`.
- Unique and foreign-key violations return `409 Conflict`; values the database rejects as too long,
  out of range or badly encoded return `422`.
- The OpenAPI schema documents error responses (`Problem`, `FieldError`, `ErrorCode`) for every
  operation.
- Every log line written while handling a request carries the request id.
- Integration tests that run against PostgreSQL, alongside the database-free unit tests.
- CI: a lint job and a test job with a PostgreSQL service and a model/migration drift check.
- An HAProxy reverse proxy in front of the production stack. It rejects request bodies over 1 MiB
  (`413`, code `payload_too_large`), adds security headers, assigns the request id, and answers
  `503` in the API's error format while the application is down. TLS termination is prepared and
  switched on with `TLS_DOMAIN`. See "Reverse proxy" in the README.
- Database time limits, tunable through `DATABASE_CONNECT_TIMEOUT` (default 5 s),
  `DATABASE_POOL_TIMEOUT` (5 s) and `DATABASE_COMMAND_TIMEOUT` (30 s). Previously a connection
  attempt could hang for 60 s and a statement had no limit.
- A self-contained production Compose file (`docker/production.yml`) with separate application
  and database secrets files.

### Changed

- The production application container is no longer published to the host; the proxy listens on
  the same default address, `127.0.0.1:8080`.
- The development stack also runs behind the proxy on `localhost:8080`, with the failed-login
  limit raised to 1000 (`LOGIN_FAILURE_LIMIT`). The application itself moved to
  `127.0.0.1:8081` for direct access.
- **Breaking:** all routes are served under `/api/v1`. Unprefixed paths no longer resolve.
- **Breaking:** creating, updating and deleting categories and products requires authentication.
  Read endpoints stay public.
- **Breaking:** product `price` is an integer amount in cents, no longer a float.
- Product `status` (`available`, `pending`, `sold`) is stored as a database enum, replacing the
  `available` column.
- **Breaking:** list endpoints validate pagination (`limit` 1 to 100, bounded `offset`) and reject
  unknown query parameters with `422`.
- **Breaking:** every error response is an RFC 9457 problem document served as
  `application/problem+json`, with a stable machine-readable `code` and the `request_id` that
  matches the `X-Request-Id` header. `detail` is still present and is always a string. See
  "Errors" in the README for the code list.
- **Breaking:** validation errors (`422`) list the invalid fields under `errors`, each with a JSON
  Pointer (`pointer`) or parameter name (`parameter`). The submitted value is no longer echoed back.
- **Breaking:** when the database is unreachable, the connection pool is exhausted or a statement
  times out, the API returns `503` (with `Retry-After` where a retry is safe) instead of `500`.
- A value the database rejects because the application sent something invalid for the schema (for
  example an unknown enum value) is reported as `500`, since it is a server fault.
- **Breaking:** a request with a valid token for an inactive account returns `403` instead of `400`.
- List endpoints return results in a deterministic order.
- CORS origins are read from `BACKEND_CORS_ORIGINS`.
- The data layer is rewritten on the SQLAlchemy 2.0 async API, with one transaction per request.
- All dependencies upgraded to their current releases, including FastAPI 0.143 (Starlette 1.7),
  SQLAlchemy 2.1, Pydantic 2.14 and PyJWT 2.15.
- Dependencies are managed with uv (`pyproject.toml` and `uv.lock`); linting and formatting use ruff.
- The Docker image is a multi-stage uv build that runs uvicorn workers as a non-root user.

### Removed

- HTTP Basic authentication scaffolding, which was never enforced.
- `requirements*.txt` and the black, isort and flake8 configuration.

### Fixed

- Routes, raw SQL, session lifecycle and Alembic configuration that prevented the app from running.
- Models, migrations and schemas now describe the same database schema.
- Application logs are emitted, and the correlation id is resolved on the request side.
- CI triggers on `main`, and the `setup-uv` action is pinned to a ref that exists.
- Unexpected errors keep the `X-Request-Id` and CORS headers and are logged with the request id,
  instead of returning a bare plain-text `500`.

### Security

- Failed logins are rate limited: after 5 failures within a minute from one address, logins from
  that address return `429` (code `rate_limited`) with `Retry-After: 60`.
- Password hashing is limited to `PASSWORD_HASH_CONCURRENCY` (default 4) simultaneous operations
  per worker, and the production `web` container has a memory limit (`WEB_MEMORY_LIMIT`, default
  `1g`), so a burst of login attempts can no longer exhaust the host's memory.
- A login with a password longer than 128 characters is rejected without being hashed.
- The upgrade moves past every advisory `pip-audit` reported against the previous PyJWT 2.13.0
  and Starlette 0.40.0.
- Logging in to an inactive account with the correct password returns the same `401` as a wrong
  password, instead of a `400` that confirmed the account and password were valid.
- Database errors are logged without the driver's message, which could contain row data such as
  emails and password hashes.
- The bootstrap error path no longer includes the superuser password in its message.
- Login releases its database connection before verifying the password hash.
