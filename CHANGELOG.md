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
- Unique and foreign-key violations return `409 Conflict`; values the database rejects return `422`.
- Integration tests that run against PostgreSQL, alongside the database-free unit tests.
- CI: a lint job and a test job with a PostgreSQL service and a model/migration drift check.
- A self-contained production Compose file (`docker/production.yml`) with separate application
  and database secrets files.

### Changed

- **Breaking:** all routes are served under `/api/v1`. Unprefixed paths no longer resolve.
- **Breaking:** creating, updating and deleting categories and products requires authentication.
  Read endpoints stay public.
- **Breaking:** product `price` is an integer amount in cents, no longer a float.
- Product `status` (`available`, `pending`, `sold`) is stored as a database enum, replacing the
  `available` column.
- **Breaking:** list endpoints validate pagination (`limit` 1 to 100, bounded `offset`) and reject
  unknown query parameters with `422`.
- List endpoints return results in a deterministic order.
- CORS origins are read from `BACKEND_CORS_ORIGINS`.
- The data layer is rewritten on the SQLAlchemy 2.0 async API, with one transaction per request.
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

### Security

- The bootstrap error path no longer includes the superuser password in its message.
- Login releases its database connection before verifying the password hash.
