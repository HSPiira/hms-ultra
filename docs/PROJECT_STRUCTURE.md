# HMS Ultra Project Structure

This document describes the organized structure of the HMS Ultra project for better code maintenance and scalability.

## Directory Structure

```
hms/
├── core/                           # Core Django application
│   ├── models.py                   # Database models
│   ├── admin.py                    # Django admin configuration
│   ├── apps.py                     # Django app configuration
│   ├── views.py                    # Django views
│   ├── migrations/                   # Database migrations
│   ├── services/                   # Business logic services
│   │   ├── __init__.py
│   │   ├── audit_trail.py
│   │   ├── billing_session.py
│   │   ├── business_logic_service.py
│   │   ├── claim_workflow.py
│   │   ├── financial_processing.py
│   │   ├── member_lifecycle.py
│   │   ├── notification_system.py
│   │   ├── provider_management.py
│   │   ├── reporting_engine.py
│   │   └── smart_api_service.py
│   ├── api/                        # API-related files
│   │   ├── __init__.py
│   │   ├── api_views.py
│   │   ├── api.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── business_rules.py
│   │   ├── monitoring.py
│   │   ├── performance_optimization.py
│   │   ├── security_hardening.py
│   │   ├── schema.py
│   │   └── repositories.py
│   └── permissions/                # Permission classes
│       ├── __init__.py
│       └── permissions.py
├── tests/                          # Test files
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_*.py
│   │   └── tests_*.py
│   ├── integration/                # Integration tests
│   │   └── __init__.py
│   └── fixtures/                   # Test fixtures
│       └── __init__.py
├── docs/                           # Documentation
│   ├── api/                        # API documentation
│   ├── database/                   # Database documentation
│   │   └── *.sql files
│   └── deployment/                  # Deployment documentation
│       └── *.md files
├── config/                         # Configuration files
│   ├── nginx/                      # Nginx configuration
│   │   └── nginx.conf
│   ├── deployment/                 # Deployment configuration
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   └── Dockerfile
│   └── production_settings.py      # Production settings
├── scripts/                        # Utility scripts
│   ├── deployment/                 # Deployment scripts
│   │   └── setup_backend.py
│   └── maintenance/                # Maintenance scripts
├── hms_ultra/                      # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── settings_development.py
│   ├── settings_production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── logs/                           # Application logs
│   └── development.log
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
└── PROJECT_STRUCTURE.md           # This file
```

## Key Changes Made

### 1. Services Organization
- **Business Logic Services**: Moved to `core/services/`
  - `audit_trail.py` - Audit trail management
  - `billing_session.py` - Billing session management
  - `business_logic_service.py` - Core business logic
  - `claim_workflow.py` - Claim processing workflow
  - `financial_processing.py` - Financial operations
  - `member_lifecycle.py` - Member management
  - `notification_system.py` - Notification services
  - `provider_management.py` - Provider management
  - `reporting_engine.py` - Reporting functionality
  - `smart_api_service.py` - Smart API integration

### 2. API Organization
- **API Files**: Moved to `core/api/`
  - `api_views.py` - REST API views
  - `api.py` - Additional API functionality
  - `serializers.py` - DRF serializers
  - `urls.py` - URL routing

### 3. Utilities Organization
- **Utility Files**: Moved to `core/utils/`
  - `business_rules.py` - Business rule definitions
  - `monitoring.py` - Application monitoring
  - `performance_optimization.py` - Performance tuning
  - `security_hardening.py` - Security utilities
  - `schema.py` - Database schema utilities
  - `repositories.py` - Data access layer

### 4. Permissions Organization
- **Permission Files**: Moved to `core/permissions/`
  - `permissions.py` - Custom permission classes

### 5. Test Organization
- **Test Files**: Moved to `tests/unit/`
  - All `test_*.py` files
  - All `tests_*.py` files

### 6. Documentation Organization
- **Documentation**: Moved to `docs/`
  - Database files to `docs/database/`
  - Markdown files to `docs/`

### 7. Configuration Organization
- **Configuration Files**: Moved to `config/`
  - Nginx config to `config/nginx/`
  - Docker files to `config/deployment/`
  - Production settings to `config/`

## Import Updates Required

After this reorganization, you'll need to update import statements in your code:

### Before:
```python
from core.audit_trail import AuditTrailFactory
from core.claim_workflow import ClaimWorkflowFactory
from core.permissions import CanViewAuditTrail
```

### After:
```python
from core.services.audit_trail import AuditTrailFactory
from core.services.claim_workflow import ClaimWorkflowFactory
from core.permissions.permissions import CanViewAuditTrail
```

## Benefits of This Structure

1. **Better Organization**: Related files are grouped together
2. **Scalability**: Easy to add new services, APIs, or utilities
3. **Maintainability**: Clear separation of concerns
4. **Team Collaboration**: Developers can work on specific areas without conflicts
5. **Testing**: Test files are properly organized by type
6. **Documentation**: All documentation is centralized
7. **Configuration**: All configuration files are in one place

## Next Steps

1. Update all import statements in the codebase
2. Update Django settings to reflect new structure
3. Update test discovery patterns
4. Update CI/CD pipelines if needed
5. Update documentation references

## Migration Commands

To update imports, you can use find and replace:

```bash
# Update service imports
find . -name "*.py" -exec sed -i 's/from core\./from core.services./g' {} \;

# Update API imports
find . -name "*.py" -exec sed -i 's/from core\.api/from core.api/g' {} \;

# Update permission imports
find . -name "*.py" -exec sed -i 's/from core\.permissions/from core.permissions.permissions/g' {} \;
```

This structure provides a solid foundation for the growing HMS Ultra project while maintaining clean separation of concerns and easy navigation.
