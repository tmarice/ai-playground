# syntax=docker/dockerfile:1

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=chatbot.settings.web \
    PORT=8000

WORKDIR /app

# System deps for psycopg + uv installer
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        libc6-dev \
        libpq-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv and create a virtualenv
RUN curl -Ls https://astral.sh/uv/install.sh | sh \
    && /root/.local/bin/uv venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH"

# Install Python dependencies first for better layer caching
COPY pyproject.toml uv.lock /app/
RUN uv pip install --no-cache-dir .

# Copy application code
COPY . /app/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000 8001

CMD ["gunicorn", "document-chatbot.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--reload"]
