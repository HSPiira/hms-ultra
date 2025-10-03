"""
Security Hardening and Best Practices
Implements comprehensive security measures
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class ISecurityValidator(ABC):
    """Interface for security validation"""
    
    @abstractmethod
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_input_sanitization(self, input_data: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_api_rate_limit(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        pass


class IEncryptionManager(ABC):
    """Interface for encryption management"""
    
    @abstractmethod
    def encrypt_sensitive_data(self, data: str) -> str:
        pass
    
    @abstractmethod
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        pass
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass


class ISecurityMonitor(ABC):
    """Interface for security monitoring"""
    
    @abstractmethod
    def detect_suspicious_activity(self, user_id: str, activity: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================

class SecurityValidator(ISecurityValidator):
    """Validates security requirements"""
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', 'admin', 'user', 'test',
            'password123', 'admin123', 'user123'
        ]
        
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_strength_score(password)
        }
    
    def validate_input_sanitization(self, input_data: str) -> Dict[str, Any]:
        """Validate and sanitize input data"""
        # Check for SQL injection patterns
        sql_patterns = [
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'create', 'alter', 'exec', 'execute', 'script'
        ]
        
        suspicious_patterns = []
        input_lower = input_data.lower()
        
        for pattern in sql_patterns:
            if pattern in input_lower:
                suspicious_patterns.append(pattern)
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        xss_detected = []
        
        for pattern in xss_patterns:
            if pattern in input_lower:
                xss_detected.append(pattern)
        
        return {
            'valid': len(suspicious_patterns) == 0 and len(xss_detected) == 0,
            'sql_patterns': suspicious_patterns,
            'xss_patterns': xss_detected,
            'sanitized_data': self._sanitize_input(input_data)
        }
    
    def validate_api_rate_limit(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Validate API rate limiting"""
        # TODO: Implement actual rate limiting logic
        # For now, return placeholder
        return {
            'allowed': True,
            'remaining_requests': 100,
            'reset_time': timezone.now() + timedelta(hours=1)
        }
    
    def _calculate_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        
        # Character variety bonus
        if any(c.isupper() for c in password):
            score += 10
        if any(c.islower() for c in password):
            score += 10
        if any(c.isdigit() for c in password):
            score += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        
        # Complexity bonus
        if len(set(password)) > len(password) * 0.7:
            score += 10
        
        return min(score, 100)
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize input data"""
        import html
        return html.escape(input_data)


class EncryptionManager(IEncryptionManager):
    """Manages encryption and hashing"""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from secret
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.secret_key.encode()).digest()
            )
            f = Fernet(key)
            
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except ImportError as e:
            logger.error(f"Cryptography library not available: {str(e)}")
            raise RuntimeError("Cryptography library is required for data encryption. Please install cryptography package.") from e
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise RuntimeError(f"Failed to encrypt sensitive data: {str(e)}") from e
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from secret
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.secret_key.encode()).digest()
            )
            f = Fernet(key)
            
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except ImportError as e:
            logger.error(f"Cryptography library not available: {str(e)}")
            raise RuntimeError("Cryptography library is required for data decryption. Please install cryptography package.") from e
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise RuntimeError(f"Failed to decrypt sensitive data: {str(e)}") from e
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except ImportError:
            # Fallback to Django's built-in hashing
            from django.contrib.auth.hashers import make_password
            return make_password(password)
        except Exception as e:
            # Log the error but NEVER return the plaintext password
            logger.exception(f"Password hashing error: {str(e)}")
            # Re-raise the exception to prevent credential leaks
            raise RuntimeError(f"Failed to hash password securely: {str(e)}") from e


class SecurityMonitor(ISecurityMonitor):
    """Monitors security events and suspicious activity"""
    
    def __init__(self):
        self.suspicious_activities = []
        self.security_events = []
    
    def detect_suspicious_activity(self, user_id: str, activity: str) -> Dict[str, Any]:
        """Detect suspicious user activity"""
        suspicious_indicators = []
        
        # Check for rapid successive actions
        recent_activities = [
            event for event in self.suspicious_activities
            if event.get('user_id') == user_id
            and event.get('timestamp') > timezone.now() - timedelta(minutes=5)
        ]
        
        if len(recent_activities) > 10:
            suspicious_indicators.append("Rapid successive actions detected")
        
        # Check for unusual access patterns
        if 'admin' in activity.lower() and user_id != 'admin':
            suspicious_indicators.append("Unauthorized admin access attempt")
        
        # Check for SQL injection attempts
        sql_keywords = ['union', 'select', 'insert', 'update', 'delete']
        if any(keyword in activity.lower() for keyword in sql_keywords):
            suspicious_indicators.append("Potential SQL injection attempt")
        
        # Log suspicious activity
        if suspicious_indicators:
            self.suspicious_activities.append({
                'user_id': user_id,
                'activity': activity,
                'indicators': suspicious_indicators,
                'timestamp': timezone.now()
            })
            
            # Log security event
            self.log_security_event('SUSPICIOUS_ACTIVITY', {
                'user_id': user_id,
                'activity': activity,
                'indicators': suspicious_indicators
            })
        
        return {
            'suspicious': len(suspicious_indicators) > 0,
            'indicators': suspicious_indicators,
            'risk_level': 'HIGH' if len(suspicious_indicators) > 2 else 'MEDIUM' if suspicious_indicators else 'LOW'
        }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security event"""
        event = {
            'event_type': event_type,
            'details': details,
            'timestamp': timezone.now(),
            'severity': self._get_event_severity(event_type)
        }
        
        self.security_events.append(event)
        
        # Log to Django logger
        logger.warning(f"Security Event: {event_type} - {details}")
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for event type"""
        severity_map = {
            'SUSPICIOUS_ACTIVITY': 'HIGH',
            'UNAUTHORIZED_ACCESS': 'CRITICAL',
            'PASSWORD_BREACH': 'CRITICAL',
            'SQL_INJECTION': 'HIGH',
            'XSS_ATTEMPT': 'HIGH',
            'RATE_LIMIT_EXCEEDED': 'MEDIUM'
        }
        return severity_map.get(event_type, 'LOW')


# =============================================================================
# BUSINESS RULE COMPOSER
# =============================================================================

class SecurityHardeningService:
    """Composes security hardening functionality"""
    
    def __init__(
        self,
        validator: ISecurityValidator,
        encryption_manager: IEncryptionManager,
        security_monitor: ISecurityMonitor
    ):
        self.validator = validator
        self.encryption_manager = encryption_manager
        self.security_monitor = security_monitor
    
    def validate_user_input(self, input_data: str, user_id: str) -> Dict[str, Any]:
        """Validate and sanitize user input"""
        # Check for suspicious activity
        activity_check = self.security_monitor.detect_suspicious_activity(
            user_id, input_data
        )
        
        # Validate input sanitization
        sanitization_check = self.validator.validate_input_sanitization(input_data)
        
        return {
            'valid': sanitization_check['valid'] and not activity_check['suspicious'],
            'sanitized_data': sanitization_check['sanitized_data'],
            'security_indicators': activity_check['indicators'],
            'risk_level': activity_check['risk_level']
        }
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        return self.validator.validate_password_strength(password)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.encryption_manager.encrypt_sensitive_data(data)
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.encryption_manager.decrypt_sensitive_data(encrypted_data)
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        return self.encryption_manager.hash_password(password)
    
    def check_api_rate_limit(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Check API rate limiting"""
        return self.validator.validate_api_rate_limit(user_id, endpoint)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        return {
            'suspicious_activities': len(self.security_monitor.suspicious_activities),
            'security_events': len(self.security_monitor.security_events),
            'recent_events': self.security_monitor.security_events[-10:] if self.security_monitor.security_events else []
        }


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class SecurityHardeningFactory:
    """Factory for creating security hardening instances"""
    
    @staticmethod
    def create_security_service() -> SecurityHardeningService:
        """Create configured security hardening service"""
        validator = SecurityValidator()
        encryption_manager = EncryptionManager()
        security_monitor = SecurityMonitor()
        
        return SecurityHardeningService(
            validator, encryption_manager, security_monitor
        )
