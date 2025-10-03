# Dockerfile for HMS Ultra Application
# Multi-stage build for production-ready container

# Use Python 3.11 slim image as base
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    django-debug-toolbar \
    django-extensions \
    ipython \
    pytest \
    pytest-django \
    pytest-cov \
    black \
    flake8 \
    isort

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=hms_ultra.settings_development"]

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r hms && useradd -r -g hms hms

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/media && \
    chown -R hms:hms /app

# Switch to non-root user
USER hms

# Collect static files
RUN python manage.py collectstatic --noinput --settings=hms_ultra.settings_production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "hms_ultra.wsgi:application"]