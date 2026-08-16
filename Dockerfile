# syntax=docker/dockerfile:1

FROM python:3.12.8-slim-bookworm AS runtime
LABEL maintainer="Gentian Demaj <gentiani101@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN python -m venv ${VIRTUAL_ENV}

WORKDIR /code

# Requirements first: source edits must not bust the dependency layer cache.
COPY requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r requirements.txt

COPY shop_api shop_api
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY scripts scripts

RUN chmod +x scripts/docker-entrypoint.sh \
 && adduser --disabled-password --no-create-home app \
 && chown -R app:app /opt/venv

USER app
EXPOSE 8080
CMD ["/code/scripts/docker-entrypoint.sh"]


FROM runtime AS dev
USER root
COPY requirements-dev.txt requirements-dev.txt
RUN python -m pip install --no-cache-dir -r requirements-dev.txt \
 && chown -R app:app /opt/venv
# pytest ini + pythonpath live here; without it in-container pytest cannot collect.
COPY pyproject.toml pyproject.toml
COPY .flake8 .flake8
COPY tests tests
USER app
