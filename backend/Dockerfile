# ── Backend Dockerfile for Render ─────────────────────────────────────────────
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend/ .

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Render sets PORT env var; default to 8000 for local docker run
ENV PORT=8000
EXPOSE $PORT

# Run with uvicorn; Render injects PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
