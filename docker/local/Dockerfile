# Pull official base image
FROM python:3.10.7
LABEL maintainer="Gentian Demaj <gentiani101@gmail.com>"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update

# Add python to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Set work directory
WORKDIR /code

# Copy project and requirements
COPY ./requirements.txt ./requirements.txt
COPY ./shop_api ./shop_api
COPY ./tests ./tests

# Install python dependencies
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    chown -R app:app /opt/venv

# Use newly created user
USER app
