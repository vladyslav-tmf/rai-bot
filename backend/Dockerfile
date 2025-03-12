ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/bin/bash" \
    --no-create-home \
    --uid "${UID}" \
    appuser \
    && mkdir -p /app /opt/.cache /opt/poetry-venv \
    && chown -R appuser:appuser /app /opt/.cache /opt/poetry-venv

# Switch to the non-privileged user
USER appuser

# Create virtual environment
RUN python -m venv /app/venv

# Install Poetry
ENV POETRY_VERSION=1.8.5
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install poetry separated from system interpreter
RUN python -m pip install -U pip setuptools \
    && python -m pip install poetry==${POETRY_VERSION}

# Copy only requirements files first
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project true

# Install dependencies
RUN poetry install --no-interaction --no-cache --without dev

# Create and copy entrypoint script
COPY --chown=appuser:appuser backend/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create backend directory and copy files
RUN mkdir -p /app/backend/app
COPY --chown=appuser:appuser backend/app /app/backend/app/
COPY --chown=appuser:appuser backend/alembic.ini /app/
COPY --chown=appuser:appuser backend/alembic /app/alembic/

# Set up Python path to include the backend directory
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose the port that the application listens on.
EXPOSE 8000

# Run the entrypoint script
CMD ["/entrypoint.sh"]
