FROM python:3.9

LABEL maintainer="gentiani101@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update

WORKDIR /code

COPY requirements.txt .

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    chown -R app:app /py

COPY . /code

ENV PATH="/py/bin:$PATH"

USER app
