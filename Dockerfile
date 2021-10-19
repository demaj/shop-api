FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
LABEL maintainer="gentiani101@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /py && \
    chown -R app:app /vol && \
    chmod -R 755 /vol

COPY . /code

ENV PATH="/py/bin:$PATH"

USER app
