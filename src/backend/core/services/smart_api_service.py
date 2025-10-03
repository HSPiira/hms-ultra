"""
Smart API Integration Service
Implements SOLID principles for external system communication
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import requests
import json
import logging

from django.conf import settings
from django.utils import timezone

from core.models import Member, Scheme, Hospital, Claim, Company


logger = logging.getLogger(__name__)


class SmartAPIStatus(Enum):
    """Smart API status enumeration"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"


class SmartAPIOperation(Enum):
    """Smart API operation enumeration"""
    CREATE_PROVIDER = "CREATE_PROVIDER"
    CREATE_MEMBER = "CREATE_MEMBER"
    CREATE_SCHEME = "CREATE_SCHEME"
    ACTIVATE_SCHEME = "ACTIVATE_SCHEME"
    RENEW_SCHEME = "RENEW_SCHEME"
    DEACTIVATE_SCHEME = "DEACTIVATE_SCHEME"
    REQUEST_CARD_REPRINT = "REQUEST_CARD_REPRINT"
    CREATE_BENEFIT = "CREATE_BENEFIT"
    CREATE_SCHEME_CATEGORY = "CREATE_SCHEME_CATEGORY"
    CHANGE_MEMBER_CATEGORY = "CHANGE_MEMBER_CATEGORY"
    PUBLISH_MONEY_ADDITION = "PUBLISH_MONEY_ADDITION"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class ISmartAPIClient(ABC):
    """Interface for Smart API client operations"""
    
    @abstractmethod
    def create_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def create_member(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def create_scheme(self, scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def activate_scheme(self, scheme_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def renew_scheme(self, scheme_id: str, renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def deactivate_scheme(self, scheme_id: str) -> Dict[str, Any]:
        pass


class ISmartAPIValidator(ABC):
    """Interface for Smart API data validation"""
    
    @abstractmethod
    def validate_provider_data(self, provider_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def validate_member_data(self, member_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def validate_scheme_data(self, scheme_data: Dict[str, Any]) -> bool:
        pass


class ISmartAPILogger(ABC):
    """Interface for Smart API operation logging"""
    
    @abstractmethod
    def log_operation(
        self, 
        operation: SmartAPIOperation, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any], 
        status: SmartAPIStatus
    ) -> None:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class SmartAPIClient(ISmartAPIClient):
    """HTTP client for Smart API communication"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Smart API"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            return {
                'status': SmartAPIStatus.SUCCESS,
                'data': response.json() if response.content else {},
                'status_code': response.status_code
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Smart API timeout for {method} {endpoint}")
            return {
                'status': SmartAPIStatus.TIMEOUT,
                'error': 'Request timeout',
                'status_code': 408
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Smart API connection error for {method} {endpoint}")
            return {
                'status': SmartAPIStatus.FAILED,
                'error': 'Connection error',
                'status_code': 503
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"Smart API HTTP error for {method} {endpoint}: {e}")
            status_code = e.response.status_code
            if status_code == 401:
                status = SmartAPIStatus.UNAUTHORIZED
            elif status_code == 404:
                status = SmartAPIStatus.NOT_FOUND
            else:
                status = SmartAPIStatus.FAILED
            
            return {
                'status': status,
                'error': str(e),
                'status_code': status_code
            }
        except Exception as e:
            logger.error(f"Smart API unexpected error for {method} {endpoint}: {e}")
            return {
                'status': SmartAPIStatus.FAILED,
                'error': str(e),
                'status_code': 500
            }
    
    def create_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create provider in Smart API"""
        return self._make_request('POST', '/api/providers', provider_data)
    
    def create_member(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create member in Smart API"""
        return self._make_request('POST', '/api/members', member_data)
    
    def create_scheme(self, scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create scheme in Smart API"""
        return self._make_request('POST', '/api/schemes', scheme_data)
    
    def activate_scheme(self, scheme_id: str) -> Dict[str, Any]:
        """Activate scheme in Smart API"""
        return self._make_request('POST', f'/api/schemes/{scheme_id}/activate')
    
    def renew_scheme(self, scheme_id: str, renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Renew scheme in Smart API"""
        return self._make_request('POST', f'/api/schemes/{scheme_id}/renew', renewal_data)
    
    def deactivate_scheme(self, scheme_id: str) -> Dict[str, Any]:
        """Deactivate scheme in Smart API"""
        return self._make_request('POST', f'/api/schemes/{scheme_id}/deactivate')


class SmartAPIValidator(ISmartAPIValidator):
    """Validates data before sending to Smart API"""
    
    def validate_provider_data(self, provider_data: Dict[str, Any]) -> bool:
        """Validate provider data for Smart API"""
        required_fields = ['name', 'reference', 'address', 'contact_person']
        
        for field in required_fields:
            if not provider_data.get(field):
                logger.warning(f"Missing required field for provider: {field}")
                return False
        
        # Validate reference format
        reference = provider_data.get('reference', '')
        if not reference or len(reference) < 3:
            logger.warning("Provider reference must be at least 3 characters")
            return False
        
        return True
    
    def validate_member_data(self, member_data: Dict[str, Any]) -> bool:
        """Validate member data for Smart API"""
        required_fields = ['name', 'employee_id', 'scheme_id', 'company_id']
        
        for field in required_fields:
            if not member_data.get(field):
                logger.warning(f"Missing required field for member: {field}")
                return False
        
        # Validate employee ID format
        employee_id = member_data.get('employee_id', '')
        if not employee_id or len(employee_id) < 3:
            logger.warning("Employee ID must be at least 3 characters")
            return False
        
        return True
    
    def validate_scheme_data(self, scheme_data: Dict[str, Any]) -> bool:
        """Validate scheme data for Smart API"""
        required_fields = ['name', 'company_id', 'limit_value']
        
        for field in required_fields:
            if not scheme_data.get(field):
                logger.warning(f"Missing required field for scheme: {field}")
                return False
        
        # Validate limit value
        limit_value = scheme_data.get('limit_value')
        if limit_value is None or limit_value <= 0:
            logger.warning("Scheme limit value must be greater than 0")
            return False
        
        return True


class SmartAPILogger(ISmartAPILogger):
    """Logs Smart API operations for audit and debugging"""
    
    def log_operation(
        self, 
        operation: SmartAPIOperation, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any], 
        status: SmartAPIStatus
    ) -> None:
        """Log Smart API operation"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'operation': operation.value,
            'request_data': request_data,
            'response_data': response_data,
            'status': status.value,
            'duration_ms': response_data.get('duration_ms', 0)
        }
        
        if status == SmartAPIStatus.SUCCESS:
            logger.info(f"Smart API {operation.value} successful: {log_entry}")
        else:
            logger.error(f"Smart API {operation.value} failed: {log_entry}")


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class SmartAPIService:
    """
    Composes Smart API operations with business rules
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        client: ISmartAPIClient,
        validator: ISmartAPIValidator,
        logger: ISmartAPILogger
    ):
        self.client = client
        self.validator = validator
        self.logger = logger
    
    def create_provider_with_validation(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create provider with validation and logging"""
        start_time = timezone.now()
        
        # Validate data
        if not self.validator.validate_provider_data(provider_data):
            return {
                'success': False,
                'error': 'Provider data validation failed',
                'status': SmartAPIStatus.FAILED
            }
        
        # Make API call
        response = self.client.create_provider(provider_data)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.CREATE_PROVIDER,
            provider_data,
            response,
            response['status']
        )
        
        return response
    
    def create_member_with_validation(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create member with validation and logging"""
        start_time = timezone.now()
        
        # Validate data
        if not self.validator.validate_member_data(member_data):
            return {
                'success': False,
                'error': 'Member data validation failed',
                'status': SmartAPIStatus.FAILED
            }
        
        # Make API call
        response = self.client.create_member(member_data)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.CREATE_MEMBER,
            member_data,
            response,
            response['status']
        )
        
        return response
    
    def create_scheme_with_validation(self, scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create scheme with validation and logging"""
        start_time = timezone.now()
        
        # Validate data
        if not self.validator.validate_scheme_data(scheme_data):
            return {
                'success': False,
                'error': 'Scheme data validation failed',
                'status': SmartAPIStatus.FAILED
            }
        
        # Make API call
        response = self.client.create_scheme(scheme_data)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.CREATE_SCHEME,
            scheme_data,
            response,
            response['status']
        )
        
        return response
    
    def activate_scheme_with_logging(self, scheme_id: str) -> Dict[str, Any]:
        """Activate scheme with logging"""
        start_time = timezone.now()
        
        # Make API call
        response = self.client.activate_scheme(scheme_id)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.ACTIVATE_SCHEME,
            {'scheme_id': scheme_id},
            response,
            response['status']
        )
        
        return response
    
    def renew_scheme_with_logging(self, scheme_id: str, renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Renew scheme with logging"""
        start_time = timezone.now()
        
        # Make API call
        response = self.client.renew_scheme(scheme_id, renewal_data)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.RENEW_SCHEME,
            {'scheme_id': scheme_id, **renewal_data},
            response,
            response['status']
        )
        
        return response
    
    def deactivate_scheme_with_logging(self, scheme_id: str) -> Dict[str, Any]:
        """Deactivate scheme with logging"""
        start_time = timezone.now()
        
        # Make API call
        response = self.client.deactivate_scheme(scheme_id)
        
        # Log operation
        duration_ms = (timezone.now() - start_time).total_seconds() * 1000
        response['duration_ms'] = duration_ms
        self.logger.log_operation(
            SmartAPIOperation.DEACTIVATE_SCHEME,
            {'scheme_id': scheme_id},
            response,
            response['status']
        )
        
        return response


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class SmartAPIServiceFactory:
    """Factory for creating Smart API service instances"""
    
    @staticmethod
    def create_smart_api_service(
        base_url: Optional[str] = None,
        timeout: int = 30
    ) -> SmartAPIService:
        """Create configured Smart API service"""
        # Get base URL from settings or use default
        if not base_url:
            base_url = getattr(settings, 'SMART_API_BASE_URL', 'http://localhost:8090')
        
        client = SmartAPIClient(base_url, timeout)
        validator = SmartAPIValidator()
        logger = SmartAPILogger()
        
        return SmartAPIService(client, validator, logger)
    
    @staticmethod
    def create_production_service() -> SmartAPIService:
        """Create production Smart API service"""
        return SmartAPIServiceFactory.create_smart_api_service(
            base_url='http://10.40.60.13:8180'
        )
    
    @staticmethod
    def create_test_service() -> SmartAPIService:
        """Create test Smart API service"""
        return SmartAPIServiceFactory.create_smart_api_service(
            base_url='http://localhost:8090'
        )
