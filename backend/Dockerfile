# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Install git (needed for untis-mcp) and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PATH="/usr/bin:${PATH}"

# Copy dependency files (cached layer)
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Clone and install untis-mcp using regular pip (not uv pip)
RUN git clone --depth 1 https://github.com/kohlsalem/untis-mcp.git /app/untis-mcp && \
    .venv/bin/pip install -e /app/untis-mcp

# Copy application code (changes frequently, so last)
COPY app ./app

# Install project
RUN uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD uv run python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health', timeout=3)" || exit 1

# Use exec form for better signal handling
CMD ["sh", "-c", "exec uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
