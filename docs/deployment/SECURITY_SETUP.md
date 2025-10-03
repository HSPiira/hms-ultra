# HMS Ultra Security Setup Guide

This document explains the security improvements made to the HMS Ultra Docker configuration to protect sensitive credentials.

## Overview

The PostgreSQL credentials and other sensitive data have been moved out of the docker-compose files to prevent accidental exposure in version control.

## Development Environment

### .env File
- **Location**: `/Users/piira/dev/hms/.env`
- **Purpose**: Contains development environment variables
- **Security**: Already in `.gitignore` to prevent accidental commits

### Environment Variables
```bash
# PostgreSQL Database Configuration
POSTGRES_DB=hms_ultra
POSTGRES_USER=hms_user
POSTGRES_PASSWORD=hms_password

# Django Database Configuration
DB_HOST=db
DB_NAME=hms_ultra
DB_USER=hms_user
DB_PASSWORD=hms_password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Django Configuration
DEBUG=1
SECRET_KEY=your-secret-key-here-change-in-production
```

### Usage
```bash
# Start development environment
cd /Users/piira/dev/hms
docker-compose -f config/deployment/docker-compose.yml up
```

## Production Environment

### Docker Secrets
Production uses Docker secrets for maximum security:

#### Setup Secrets
```bash
# Run the setup script
./scripts/deployment/setup-docker-secrets.sh
```

#### Created Secrets
- `postgres_db` - Database name
- `postgres_user` - Database user
- `postgres_password` - Database password (auto-generated)
- `django_secret_key` - Django secret key (auto-generated)
- `redis_password` - Redis password (auto-generated)

#### Secret Management
```bash
# List secrets
docker secret ls

# Remove a secret
docker secret rm <secret_name>

# View secret content (requires root)
docker secret inspect <secret_name>
```

### Production Usage
```bash
# Start production environment
docker-compose -f config/deployment/docker-compose.prod.yml up
```

## Database Initialization

### init.sql File
- **Location**: `/Users/piira/dev/hms/init.sql`
- **Purpose**: PostgreSQL initialization script
- **Contents**:
  - Enables required extensions (uuid-ossp, pg_trgm, unaccent)
  - Creates utility functions
  - Sets up initial permissions

### Usage
The init.sql file is automatically mounted into the PostgreSQL container and runs on first startup.

## Security Benefits

### 1. **Credential Protection**
- No hardcoded passwords in version control
- Environment-specific configuration
- Automatic secret generation for production

### 2. **Access Control**
- Secrets have restricted permissions (600)
- External secrets prevent accidental exposure
- Separate development and production configurations

### 3. **Audit Trail**
- All secret operations are logged
- Clear separation between environments
- Documented setup procedures

## File Structure

```
hms/
├── .env                          # Development environment variables
├── init.sql                      # PostgreSQL initialization
├── scripts/deployment/
│   └── setup-docker-secrets.sh   # Production secret setup
├── config/deployment/
│   ├── docker-compose.yml        # Development configuration
│   └── docker-compose.prod.yml   # Production configuration
└── docs/deployment/
    └── SECURITY_SETUP.md         # This documentation
```

## Troubleshooting

### Common Issues

#### 1. Missing .env File
```bash
# Error: Environment variable not set
# Solution: Ensure .env file exists in project root
ls -la .env
```

#### 2. Docker Secrets Not Found
```bash
# Error: Secret not found
# Solution: Run the setup script
./scripts/deployment/setup-docker-secrets.sh
```

#### 3. Permission Denied
```bash
# Error: Permission denied on secrets
# Solution: Check file permissions
chmod 600 secrets/*
```

### Verification Commands

#### Check Environment Variables
```bash
# Verify .env file exists and has correct content
cat .env | grep -E "(POSTGRES|DB_)"
```

#### Check Docker Secrets
```bash
# List all secrets
docker secret ls

# Verify secret content
docker secret inspect postgres_password
```

#### Test Database Connection
```bash
# Test PostgreSQL connection
docker-compose -f config/deployment/docker-compose.yml exec db psql -U hms_user -d hms_ultra -c "SELECT version();"
```

## Best Practices

### 1. **Development**
- Use `.env` file for local development
- Never commit `.env` to version control
- Use strong passwords even in development

### 2. **Production**
- Use Docker secrets for all sensitive data
- Rotate secrets regularly
- Monitor secret access logs

### 3. **General**
- Document all environment variables
- Use different credentials for each environment
- Regularly audit access permissions

## Migration from Hardcoded Credentials

### Before (Insecure)
```yaml
environment:
  POSTGRES_DB: hms_ultra
  POSTGRES_USER: hms_user
  POSTGRES_PASSWORD: hms_password
```

### After (Secure)
```yaml
env_file:
  - .env
environment:
  POSTGRES_DB: ${POSTGRES_DB}
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

## Support

For issues or questions regarding the security setup:
1. Check this documentation
2. Verify file permissions
3. Test with minimal configuration
4. Review Docker logs for errors
