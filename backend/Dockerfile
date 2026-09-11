# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Install git for uvx to install from git repositories
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PATH="/usr/bin:${PATH}"

# Install dependencies first so this layer is cached when only app code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY app ./app

RUN uv sync --frozen --no-dev

# Create a wrapper script for uvx that ensures git is in PATH
RUN echo '#!/bin/sh\nexport PATH="/usr/bin:$PATH"\nexec /root/.cargo/bin/uvx "$@"' > /usr/local/bin/uvx && chmod +x /usr/local/bin/uvx

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD uv run python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health', timeout=3)" || exit 1

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
