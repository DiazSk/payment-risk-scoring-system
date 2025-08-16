# Multi-stage build for E-Commerce Fraud Detection System
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy requirements first for better caching
COPY --chown=app:app requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Add user site-packages to PATH
ENV PATH=/home/app/.local/bin:$PATH

# Development stage
FROM base as development

# Copy all source code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p data/raw data/processed models logs config

# Copy configuration files
COPY --chown=app:app config/ config/

# Expose port for development
EXPOSE 8000

# Development command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy only necessary files for production
COPY --chown=app:app src/ src/
COPY --chown=app:app app/ app/
COPY --chown=app:app config/ config/
COPY --chown=app:app models/ models/
COPY --chown=app:app dashboard/ dashboard/

# Create necessary directories
RUN mkdir -p data/raw data/processed logs

# Copy any pre-trained models (if they exist)
# COPY --chown=app:app models/*.pkl models/ 2>/dev/null || :

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]

# Testing stage
FROM development as testing

# Install additional testing dependencies
RUN pip install --user pytest pytest-cov pytest-asyncio httpx

# Copy test files
COPY --chown=app:app tests/ tests/

# Run tests
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov=app"]