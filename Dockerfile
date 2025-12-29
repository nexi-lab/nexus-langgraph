# Nexus LangGraph Agent Server - Production Dockerfile
# Multi-stage build for optimal image size

FROM python:3.13-slim AS builder

# Install build dependencies (including build-essential for Rust linking)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy project files
WORKDIR /app
COPY pyproject.toml ./
COPY *.py ./
COPY langgraph.json ./
COPY agents ./agents
COPY shared ./shared

# Install dependencies (including nexus-ai-fs from PyPI)
RUN uv pip install --system .

# ============================================
# Production image
# ============================================
FROM python:3.13-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages and CLI tools from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application files
WORKDIR /app
COPY *.py ./
COPY langgraph.json ./
COPY agents ./agents
COPY shared ./shared

# Create non-root user for security
RUN useradd -r -m -u 1000 -s /bin/bash nexus && \
    chown -R nexus:nexus /app

# Create .langgraph_api directory with proper permissions
RUN mkdir -p /app/.langgraph_api && chown -R nexus:nexus /app/.langgraph_api

# Switch to non-root user
USER nexus

# Environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    LANGGRAPH_HOST=0.0.0.0 \
    LANGGRAPH_PORT=2024

# Expose port
EXPOSE 2024

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${LANGGRAPH_PORT}/ok || exit 1

# Tell Docker to send SIGINT instead of SIGTERM for graceful shutdown
# Uvicorn handles SIGINT properly and triggers the lifespan shutdown
STOPSIGNAL SIGINT

# Run the LangGraph server
# Use exec to make langgraph the PID 1 process (not sh)
CMD ["sh", "-c", "exec langgraph dev --host ${LANGGRAPH_HOST} --port ${LANGGRAPH_PORT}"]
