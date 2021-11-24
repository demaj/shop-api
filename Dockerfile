# Pull official base image
FROM python:3.9

LABEL maintainer="gentiani101@gmail.com"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update

# Set work directory
WORKDIR /code

COPY requirements.txt .

# Install dependencies
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    chown -R app:app /py

# Copy project
COPY . /code

# Add python to PATH
ENV PATH="/py/bin:$PATH"

# Use newly created user
USER app
