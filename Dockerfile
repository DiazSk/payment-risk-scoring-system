# Production Dockerfile for E-Commerce Fraud Detection System
FROM python:3.11-slim as base

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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app /app/logs /app/reports \
    && chown -R appuser:appuser /app
USER appuser

# Copy requirements first for better caching
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Add user site-packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Development stage
FROM base as development

# Copy all source code for development
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy only production-necessary files
COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser models/ models/

# Create necessary directories
RUN mkdir -p logs reports

# Health check specific to our API
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Install gunicorn for production
RUN pip install --user gunicorn

# Production command with gunicorn for better performance
CMD ["python", "-m", "gunicorn", "app.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

# Testing stage
FROM development as testing

# Install testing dependencies
RUN pip install --user pytest pytest-asyncio httpx

# Copy test files
COPY --chown=appuser:appuser test_api.py .
COPY --chown=appuser:appuser example_client.py .

# Wait for API to be ready and then run tests
CMD ["sh", "-c", "python app/main.py & sleep 10 && python test_api.py"]