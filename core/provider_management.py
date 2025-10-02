"""
Provider (Hospital) Management Business Logic
Implements SOLID principles for provider lifecycle and relationship management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from django.db import transaction, models
from django.utils import timezone

from .models import (
    Hospital, HospitalBranch, HospitalDoctor, HospitalMedicine, 
    HospitalService, HospitalLabTest, Medicine, Service, LabTest
)
from .smart_api_service import SmartAPIServiceFactory


class ProviderStatus(Enum):
    """Provider status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class ProviderType(Enum):
    """Provider type enumeration"""
    HOSPITAL = "HOSPITAL"
    CLINIC = "CLINIC"
    PHARMACY = "PHARMACY"
    LABORATORY = "LABORATORY"
    SPECIALIST = "SPECIALIST"


class ProviderAction(Enum):
    """Provider action enumeration"""
    REGISTER = "REGISTER"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"
    SUSPEND = "SUSPEND"
    TERMINATE = "TERMINATE"
    UPDATE_PRICING = "UPDATE_PRICING"
    ADD_SERVICE = "ADD_SERVICE"
    REMOVE_SERVICE = "REMOVE_SERVICE"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IProviderValidator(ABC):
    """Interface for provider validation"""
    
    @abstractmethod
    def validate_provider_data(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_provider_eligibility(self, provider_id: str) -> Dict[str, Any]:
        pass


class IProviderPricingManager(ABC):
    """Interface for provider pricing management"""
    
    @abstractmethod
    def update_service_pricing(
        self, 
        provider_id: str, 
        service_id: str, 
        new_price: Decimal
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_pricing_agreement(
        self, 
        provider_id: str, 
        service_id: str, 
        proposed_price: Decimal
    ) -> Dict[str, Any]:
        pass


class IProviderServiceManager(ABC):
    """Interface for provider service management"""
    
    @abstractmethod
    def add_service_to_provider(
        self, 
        provider_id: str, 
        service_id: str, 
        pricing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def remove_service_from_provider(
        self, 
        provider_id: str, 
        service_id: str
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_provider_services(self, provider_id: str) -> List[Dict[str, Any]]:
        pass


class IProviderLifecycleManager(ABC):
    """Interface for provider lifecycle management"""
    
    @abstractmethod
    def register_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def activate_provider(self, provider_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def deactivate_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def suspend_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class ProviderValidator(IProviderValidator):
    """Validates provider data and eligibility"""
    
    def validate_provider_data(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provider registration data"""
        required_fields = [
            'hospital_name', 'hospital_reference', 'hospital_address',
            'contact_person', 'hospital_phone_number'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not provider_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'errors': [f'Missing required field: {field}' for field in missing_fields]
            }
        
        # Validate hospital reference uniqueness
        reference = provider_data.get('hospital_reference')
        if reference and Hospital.objects.filter(hospital_reference=reference).exists():
            return {
                'valid': False,
                'errors': ['Hospital reference already exists']
            }
        
        # Validate phone number format
        phone = provider_data.get('hospital_phone_number')
        if phone and len(phone) < 10:
            return {
                'valid': False,
                'errors': ['Phone number must be at least 10 digits']
            }
        
        return {'valid': True, 'errors': []}
    
    def validate_provider_eligibility(self, provider_id: str) -> Dict[str, Any]:
        """Validate provider eligibility for services"""
        try:
            provider = Hospital.objects.get(id=provider_id)
            
            # Check if provider is active
            if provider.status != 'ACTIVE':
                return {
                    'eligible': False,
                    'reason': f'Provider is not active. Current status: {provider.status}'
                }
            
            # Check if provider has required services
            service_count = HospitalService.objects.filter(hospital_id=provider_id).count()
            if service_count == 0:
                return {
                    'eligible': False,
                    'reason': 'Provider has no services configured'
                }
            
            return {
                'eligible': True,
                'reason': 'Provider is eligible for services'
            }
            
        except Hospital.DoesNotExist:
            return {
                'eligible': False,
                'reason': 'Provider not found'
            }


class ProviderPricingManager(IProviderPricingManager):
    """Manages provider pricing agreements"""
    
    def update_service_pricing(
        self, 
        provider_id: str, 
        service_id: str, 
        new_price: Decimal
    ) -> Dict[str, Any]:
        """Update service pricing for provider"""
        try:
            # Validate price
            if new_price <= 0:
                return {
                    'success': False,
                    'error': 'Price must be greater than zero'
                }
            
            # Update hospital service pricing
            hospital_service = HospitalService.objects.filter(
                hospital_id=provider_id,
                service_id=service_id
            ).first()
            
            if not hospital_service:
                return {
                    'success': False,
                    'error': 'Service not found for this provider'
                }
            
            # Update price
            hospital_service.amount = new_price
            hospital_service.effective_date = timezone.now().date()
            hospital_service.save()
            
            return {
                'success': True,
                'message': 'Service pricing updated successfully',
                'new_price': new_price
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_pricing_agreement(
        self, 
        provider_id: str, 
        service_id: str, 
        proposed_price: Decimal
    ) -> Dict[str, Any]:
        """Validate pricing agreement against business rules"""
        try:
            # Get current pricing
            hospital_service = HospitalService.objects.filter(
                hospital_id=provider_id,
                service_id=service_id
            ).first()
            
            if not hospital_service:
                return {
                    'valid': False,
                    'reason': 'Service not found for this provider'
                }
            
            current_price = hospital_service.amount
            
            # Check price variance (max 20% increase)
            if current_price > 0:
                variance = (proposed_price - current_price) / current_price
                if variance > 0.2:  # 20% increase limit
                    return {
                        'valid': False,
                        'reason': f'Price increase exceeds 20% limit. Variance: {variance:.1%}'
                    }
            
            return {
                'valid': True,
                'reason': 'Pricing agreement is valid'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': str(e)
            }


class ProviderServiceManager(IProviderServiceManager):
    """Manages provider service relationships"""
    
    def add_service_to_provider(
        self, 
        provider_id: str, 
        service_id: str, 
        pricing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add service to provider with pricing"""
        try:
            # Check if service already exists for provider
            existing = HospitalService.objects.filter(
                hospital_id=provider_id,
                service_id=service_id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'error': 'Service already exists for this provider'
                }
            
            # Create hospital service relationship
            hospital_service = HospitalService.objects.create(
                hospital_id=provider_id,
                service_id=service_id,
                amount=pricing_data.get('amount', Decimal('0')),
                available=pricing_data.get('available', True),
                effective_date=pricing_data.get('effective_date', timezone.now().date())
            )
            
            return {
                'success': True,
                'message': 'Service added to provider successfully',
                'hospital_service_id': str(hospital_service.id)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_service_from_provider(
        self, 
        provider_id: str, 
        service_id: str
    ) -> Dict[str, Any]:
        """Remove service from provider"""
        try:
            hospital_service = HospitalService.objects.filter(
                hospital_id=provider_id,
                service_id=service_id
            ).first()
            
            if not hospital_service:
                return {
                    'success': False,
                    'error': 'Service not found for this provider'
                }
            
            # Soft delete by setting available to False
            hospital_service.available = False
            hospital_service.save()
            
            return {
                'success': True,
                'message': 'Service removed from provider successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_provider_services(self, provider_id: str) -> List[Dict[str, Any]]:
        """Get all services for a provider"""
        try:
            services = HospitalService.objects.filter(
                hospital_id=provider_id,
                available=True
            ).select_related('service')
            
            return [
                {
                    'service_id': str(service.service_id),
                    'service_name': service.service.service_name,
                    'amount': service.amount,
                    'available': service.available,
                    'effective_date': service.effective_date
                }
                for service in services
            ]
            
        except Exception as e:
            return []


class ProviderLifecycleManager(IProviderLifecycleManager):
    """Manages provider lifecycle operations"""
    
    def __init__(self, validator: IProviderValidator):
        self.validator = validator
        self.smart_api = SmartAPIServiceFactory.create_smart_api_service()
    
    @transaction.atomic
    def register_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new provider"""
        try:
            # Validate provider data
            validation_result = self.validator.validate_provider_data(provider_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
            
            # Create provider record
            provider = Hospital.objects.create(
                hospital_name=provider_data['hospital_name'],
                hospital_reference=provider_data['hospital_reference'],
                hospital_address=provider_data['hospital_address'],
                contact_person=provider_data['contact_person'],
                hospital_phone_number=provider_data['hospital_phone_number'],
                hospital_email=provider_data.get('hospital_email'),
                hospital_website=provider_data.get('hospital_website'),
                status='PENDING_APPROVAL'
            )
            
            # Register with Smart API
            smart_api_data = {
                'name': provider.hospital_name,
                'reference': provider.hospital_reference,
                'address': provider.hospital_address,
                'contact_person': provider.contact_person,
                'phone': provider.hospital_phone_number,
                'email': provider.hospital_email,
                'website': provider.hospital_website
            }
            
            smart_api_result = self.smart_api.create_provider_with_validation(smart_api_data)
            
            if smart_api_result['status'].value != 'SUCCESS':
                # Rollback provider creation if Smart API fails
                provider.delete()
                return {
                    'success': False,
                    'error': f'Smart API registration failed: {smart_api_result.get("error")}'
                }
            
            return {
                'success': True,
                'message': 'Provider registered successfully',
                'provider_id': str(provider.id),
                'smart_api_result': smart_api_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @transaction.atomic
    def activate_provider(self, provider_id: str) -> Dict[str, Any]:
        """Activate provider"""
        try:
            provider = Hospital.objects.get(id=provider_id)
            
            if provider.status != 'PENDING_APPROVAL':
                return {
                    'success': False,
                    'error': f'Provider must be pending approval to activate. Current status: {provider.status}'
                }
            
            # Update status
            provider.status = 'ACTIVE'
            provider.save()
            
            return {
                'success': True,
                'message': 'Provider activated successfully',
                'provider_id': provider_id
            }
            
        except Hospital.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }
    
    @transaction.atomic
    def deactivate_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        """Deactivate provider"""
        try:
            provider = Hospital.objects.get(id=provider_id)
            
            if provider.status == 'INACTIVE':
                return {
                    'success': False,
                    'error': 'Provider is already inactive'
                }
            
            # Update status
            provider.status = 'INACTIVE'
            provider.deactivation_reason = reason
            provider.deactivation_date = timezone.now()
            provider.save()
            
            return {
                'success': True,
                'message': 'Provider deactivated successfully',
                'provider_id': provider_id,
                'reason': reason
            }
            
        except Hospital.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }
    
    @transaction.atomic
    def suspend_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        """Suspend provider"""
        try:
            provider = Hospital.objects.get(id=provider_id)
            
            if provider.status != 'ACTIVE':
                return {
                    'success': False,
                    'error': f'Only active providers can be suspended. Current status: {provider.status}'
                }
            
            # Update status
            provider.status = 'SUSPENDED'
            provider.suspension_reason = reason
            provider.suspension_date = timezone.now()
            provider.save()
            
            return {
                'success': True,
                'message': 'Provider suspended successfully',
                'provider_id': provider_id,
                'reason': reason
            }
            
        except Hospital.DoesNotExist:
            return {
                'success': False,
                'error': 'Provider not found'
            }


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class ProviderManagementService:
    """
    Composes provider management operations
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        validator: IProviderValidator,
        pricing_manager: IProviderPricingManager,
        service_manager: IProviderServiceManager,
        lifecycle_manager: IProviderLifecycleManager
    ):
        self.validator = validator
        self.pricing_manager = pricing_manager
        self.service_manager = service_manager
        self.lifecycle_manager = lifecycle_manager
    
    def register_new_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new provider with complete workflow"""
        return self.lifecycle_manager.register_provider(provider_data)
    
    def activate_provider(self, provider_id: str) -> Dict[str, Any]:
        """Activate provider"""
        return self.lifecycle_manager.activate_provider(provider_id)
    
    def deactivate_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        """Deactivate provider"""
        return self.lifecycle_manager.deactivate_provider(provider_id, reason)
    
    def suspend_provider(self, provider_id: str, reason: str) -> Dict[str, Any]:
        """Suspend provider"""
        return self.lifecycle_manager.suspend_provider(provider_id, reason)
    
    def add_service_to_provider(
        self, 
        provider_id: str, 
        service_id: str, 
        pricing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add service to provider"""
        return self.service_manager.add_service_to_provider(
            provider_id, service_id, pricing_data
        )
    
    def remove_service_from_provider(
        self, 
        provider_id: str, 
        service_id: str
    ) -> Dict[str, Any]:
        """Remove service from provider"""
        return self.service_manager.remove_service_from_provider(
            provider_id, service_id
        )
    
    def update_service_pricing(
        self, 
        provider_id: str, 
        service_id: str, 
        new_price: Decimal
    ) -> Dict[str, Any]:
        """Update service pricing"""
        return self.pricing_manager.update_service_pricing(
            provider_id, service_id, new_price
        )
    
    def get_provider_services(self, provider_id: str) -> List[Dict[str, Any]]:
        """Get provider services"""
        return self.service_manager.get_provider_services(provider_id)
    
    def validate_provider_eligibility(self, provider_id: str) -> Dict[str, Any]:
        """Validate provider eligibility"""
        return self.validator.validate_provider_eligibility(provider_id)


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class ProviderManagementFactory:
    """Factory for creating provider management instances"""
    
    @staticmethod
    def create_provider_management_service() -> ProviderManagementService:
        """Create configured provider management service"""
        validator = ProviderValidator()
        pricing_manager = ProviderPricingManager()
        service_manager = ProviderServiceManager()
        lifecycle_manager = ProviderLifecycleManager(validator)
        
        return ProviderManagementService(
            validator, pricing_manager, service_manager, lifecycle_manager
        )
