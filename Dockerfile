# Pull official base image
FROM python:3.11.1
LABEL maintainer="Gentian Demaj <gentiani101@gmail.com>"

# Update system dependencies
RUN apt-get update

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv

# Add python to PATH
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

# Create python virtual environment
RUN python -m venv ${VIRTUAL_ENV}

# Set work directory
WORKDIR /code

# Copy project and requirements
COPY requirements.txt requirements.txt
COPY shop_api shop_api
COPY tests tests
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY docker-entrypoint.sh docker-entrypoint.sh

# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    chown -R app:app /opt/venv && \
    chmod +x docker-entrypoint.sh

# Use newly created user
USER app

# Sanity check
RUN python --version

# ENTRYPOINT [ "./docker-entrypoint.sh" ]
