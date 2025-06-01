# Mental Wellness Coach - Python Flask Backend Dockerfile
# Multi-stage production build for Python Flask application

# =============================================================================
# Base Stage - Python Runtime
# =============================================================================
FROM python:3.11-slim as base

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN addgroup --gid 1001 --system flask && \
    adduser --uid 1001 --system --gid 1001 flask

# =============================================================================
# Dependencies Stage
# =============================================================================
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# Development Stage
# =============================================================================
FROM dependencies as development

# Copy application code
COPY --chown=flask:flask . .

# Create necessary directories
RUN mkdir -p /app/logs && chown -R flask:flask /app/logs

# Switch to application user
USER flask

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Start development server
CMD ["python", "app.py"]

# =============================================================================
# Production Stage
# =============================================================================
FROM dependencies as production

# Copy application code
COPY --chown=flask:flask . .

# Create necessary directories
RUN mkdir -p /app/logs && chown -R flask:flask /app/logs

# Remove development files
RUN rm -rf tests/ *.md .git*

# Switch to application user
USER flask

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Start production server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "30", "app:app"]

# =============================================================================
# Labels for metadata
# =============================================================================
LABEL maintainer="Mental Wellness Coach Team <dev@mentalwellnesscoach.ai>"
LABEL version="1.0.0"
LABEL description="Mental Wellness Coach Backend API"
LABEL org.opencontainers.image.title="Mental Wellness Coach Backend"
LABEL org.opencontainers.image.description="Privacy-first AI agent backend for mental health support"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-org/mental-wellness-coach"
LABEL org.opencontainers.image.licenses="MIT" 