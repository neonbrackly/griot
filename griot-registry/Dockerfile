# =============================================================================
# Griot Registry Dockerfile
# =============================================================================
# Multi-stage build for the FastAPI backend
# Must be built from the monorepo root to access griot-core dependency:
#   docker build -f griot-registry/Dockerfile -t griot-registry .
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace configuration
COPY pyproject.toml uv.lock* ./

# Copy griot-core (local dependency)
COPY griot-core/ ./griot-core/

# Copy griot-registry
COPY griot-registry/ ./griot-registry/

# Install dependencies using UV
# Create virtual environment and install the registry package
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install ./griot-core && \
    uv pip install ./griot-registry

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash griot

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Create data directory for filesystem storage
RUN mkdir -p /app/data/contracts && chown -R griot:griot /app

# Switch to non-root user
USER griot

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Default configuration (override via docker-compose or -e flags)
    GRIOT_REGISTRY_HOST=0.0.0.0 \
    GRIOT_REGISTRY_PORT=8000 \
    GRIOT_REGISTRY_STORAGE_PATH=/app/data/contracts

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Run the server
CMD ["griot-registry"]
