# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime
LABEL maintainer="Gentian Demaj <gentiani101@gmail.com>"

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONUNBUFFERED=1 \
    PATH="/code/.venv/bin:$PATH"

WORKDIR /code

# Runtime dependencies only, cached on the lockfile + pyproject (package=false, so
# the project source is not needed here — editing code never busts this layer).
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

COPY shop_api shop_api
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY scripts scripts

RUN chmod +x scripts/docker-entrypoint.sh \
 && adduser --disabled-password --no-create-home app \
 && chown -R app:app /code/.venv
USER app
EXPOSE 8080
CMD ["/code/scripts/docker-entrypoint.sh"]


FROM runtime AS dev
# /code is root-owned; give ruff a cache dir the app user can write.
ENV RUFF_CACHE_DIR=/tmp/ruff-cache
USER root
# Add the dev group (ruff, pytest, ...) to the same venv, and the pytest config.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked
COPY pyproject.toml pyproject.toml
COPY tests tests
RUN chown -R app:app /code/.venv
USER app
