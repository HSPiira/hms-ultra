#!/usr/bin/env python
"""
Script to update import statements after project reorganization
"""

import os
import re
from pathlib import Path

def update_imports():
    """Update import statements to reflect new directory structure"""
    
    print("Updating import statements after project reorganization...")
    print("=" * 60)
    
    # Define the import mappings
    import_mappings = {
        # Services imports
        r'from core\.audit_trail import': 'from core.services.audit_trail import',
        r'from core\.billing_session import': 'from core.services.billing_session import',
        r'from core\.business_logic_service import': 'from core.services.business_logic_service import',
        r'from core\.claim_workflow import': 'from core.services.claim_workflow import',
        r'from core\.financial_processing import': 'from core.services.financial_processing import',
        r'from core\.member_lifecycle import': 'from core.services.member_lifecycle import',
        r'from core\.notification_system import': 'from core.services.notification_system import',
        r'from core\.provider_management import': 'from core.services.provider_management import',
        r'from core\.reporting_engine import': 'from core.services.reporting_engine import',
        r'from core\.smart_api_service import': 'from core.services.smart_api_service import',
        
        # API imports
        r'from core\.api_views import': 'from core.api.api_views import',
        r'from core\.api import': 'from core.api.api import',
        r'from core\.serializers import': 'from core.api.serializers import',
        r'from core\.urls import': 'from core.api.urls import',
        
        # Utils imports
        r'from core\.business_rules import': 'from core.utils.business_rules import',
        r'from core\.monitoring import': 'from core.utils.monitoring import',
        r'from core\.performance_optimization import': 'from core.utils.performance_optimization import',
        r'from core\.security_hardening import': 'from core.utils.security_hardening import',
        r'from core\.schema import': 'from core.utils.schema import',
        r'from core\.repositories import': 'from core.utils.repositories import',
        
        # Permissions imports
        r'from core\.permissions import': 'from core.permissions.permissions import',
    }
    
    # Files to update
    files_to_update = [
        'core/services/',
        'core/api/',
        'core/utils/',
        'core/permissions/',
        'tests/',
        'hms_ultra/',
        'manage.py'
    ]
    
    updated_files = 0
    total_replacements = 0
    
    for file_pattern in files_to_update:
        if os.path.isfile(file_pattern):
            # Single file
            files = [file_pattern]
        else:
            # Directory - find all Python files
            files = []
            for root, dirs, filenames in os.walk(file_pattern):
                for filename in filenames:
                    if filename.endswith('.py'):
                        files.append(os.path.join(root, filename))
        
        for file_path in files:
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                file_replacements = 0
                
                # Apply all import mappings
                for old_pattern, new_pattern in import_mappings.items():
                    if re.search(old_pattern, content):
                        content = re.sub(old_pattern, new_pattern, content)
                        file_replacements += 1
                
                # Write back if changes were made
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_files += 1
                    total_replacements += file_replacements
                    print(f"✓ Updated {file_path} ({file_replacements} replacements)")
                
            except Exception as e:
                print(f"✗ Error updating {file_path}: {e}")
    
    print()
    print("=" * 60)
    print(f"✓ Import update completed!")
    print(f"✓ Updated {updated_files} files")
    print(f"✓ Made {total_replacements} total replacements")
    
    return True

if __name__ == '__main__':
    update_imports()
