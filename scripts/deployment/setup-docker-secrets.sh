#!/bin/bash
# Setup Docker Secrets for HMS Ultra Production
# This script creates Docker secrets for sensitive data

set -e

echo "Setting up Docker secrets for HMS Ultra production..."

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Generate secure passwords if they don't exist
if [ ! -f "secrets/postgres_password" ]; then
    echo "Generating PostgreSQL password..."
    openssl rand -base64 32 > secrets/postgres_password
    chmod 600 secrets/postgres_password
fi

if [ ! -f "secrets/django_secret_key" ]; then
    echo "Generating Django secret key..."
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > secrets/django_secret_key
    chmod 600 secrets/django_secret_key
fi

if [ ! -f "secrets/redis_password" ]; then
    echo "Generating Redis password..."
    openssl rand -base64 32 > secrets/redis_password
    chmod 600 secrets/redis_password
fi

# Create Docker secrets
echo "Creating Docker secrets..."

# PostgreSQL secrets
docker secret create postgres_db "hms_ultra" 2>/dev/null || echo "postgres_db secret already exists"
docker secret create postgres_user "hms_user" 2>/dev/null || echo "postgres_user secret already exists"
docker secret create postgres_password secrets/postgres_password 2>/dev/null || echo "postgres_password secret already exists"

# Django secrets
docker secret create django_secret_key secrets/django_secret_key 2>/dev/null || echo "django_secret_key secret already exists"

# Redis secrets
docker secret create redis_password secrets/redis_password 2>/dev/null || echo "redis_password secret already exists"

echo "Docker secrets setup complete!"
echo ""
echo "Created secrets:"
echo "- postgres_db"
echo "- postgres_user" 
echo "- postgres_password"
echo "- django_secret_key"
echo "- redis_password"
echo ""
echo "To view secrets: docker secret ls"
echo "To remove secrets: docker secret rm <secret_name>"
