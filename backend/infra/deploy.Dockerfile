FROM python:3.12-slim-bullseye

WORKDIR /app

ENV PROJECT_ROOT=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock README.md /app/
COPY /libs /app/libs
COPY /tools /app/tools

# Install Python dependencies (production only)
RUN uv sync --frozen --no-dev

# Copy application code
COPY /app /app/app
COPY /alembic.ini /app/alembic.ini

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
