FROM python:3.14.0-slim-bookworm

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update \
  && apt-get -y install netcat-traditional gcc postgresql \
  && apt-get clean

# Install dependencies first (better caching)
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --extra dev --extra test

# Copy the project code
COPY . .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra dev --extra test

# Ensure the virtual environment is used
ENV PATH="/usr/src/app/.venv/bin:$PATH"

RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]