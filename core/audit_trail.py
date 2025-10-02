"""
Audit Trail and Logging System
Implements SOLID principles for comprehensive audit and logging
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import json
import logging

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Claim, Member, Hospital, Scheme, Company


logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """
    Audit action enumeration.
    
    Defines all possible actions that can be audited in the system.
    Used to categorize different types of user and system activities.
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PAY = "PAY"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


class AuditLevel(Enum):
    """
    Audit level enumeration.
    
    Defines the severity levels for audit events.
    Used to categorize the importance and urgency of audit entries.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditStatus(Enum):
    """
    Audit status enumeration.
    
    Defines the possible outcomes of audited actions.
    Used to track whether an action completed successfully or failed.
    """
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IAuditLogger(ABC):
    """Interface for audit logging"""
    
    @abstractmethod
    def log_audit_event(
        self, 
        action: AuditAction, 
        entity_type: str, 
        entity_id: str, 
        user_id: str, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def log_security_event(
        self, 
        event_type: str, 
        user_id: str, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass


class IAuditQuery(ABC):
    """Interface for audit querying"""
    
    @abstractmethod
    def get_audit_trail(
        self, 
        entity_type: str, 
        entity_id: str
    ) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_user_audit_trail(
        self, 
        user_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_audit_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        pass


class IAuditExporter(ABC):
    """Interface for audit export"""
    
    @abstractmethod
    def export_audit_trail(
        self, 
        start_date: date, 
        end_date: date, 
        format_type: str
    ) -> str:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class AuditLogger(IAuditLogger):
    """Handles audit logging operations"""
    
    def log_audit_event(
        self, 
        action: AuditAction, 
        entity_type: str, 
        entity_id: str, 
        user_id: str, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log audit event"""
        try:
            # Create audit log entry
            audit_entry = {
                'timestamp': timezone.now().isoformat(),
                'action': action.value,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'user_id': user_id,
                'details': details,
                'level': AuditLevel.INFO.value,
                'status': AuditStatus.SUCCESS.value
            }
            
            # Log to Django logger
            logger.info(f"Audit Event: {json.dumps(audit_entry)}")
            
            # TODO: Store in database audit table
            # For now, just log to file
            
            return {
                'success': True,
                'audit_id': f"audit_{entity_type}_{entity_id}_{timezone.now().timestamp()}",
                'message': 'Audit event logged successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_security_event(
        self, 
        event_type: str, 
        user_id: str, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log security event"""
        try:
            security_entry = {
                'timestamp': timezone.now().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'details': details,
                'level': AuditLevel.WARNING.value,
                'status': AuditStatus.SUCCESS.value
            }
            
            # Log to Django logger
            logger.warning(f"Security Event: {json.dumps(security_entry)}")
            
            return {
                'success': True,
                'security_id': f"security_{event_type}_{user_id}_{timezone.now().timestamp()}",
                'message': 'Security event logged successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class AuditQuery(IAuditQuery):
    """Handles audit querying operations"""
    
    def get_audit_trail(
        self, 
        entity_type: str, 
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """Get audit trail for specific entity"""
        try:
            # TODO: Implement actual database query
            # For now, return placeholder data
            return [
                {
                    'timestamp': timezone.now().isoformat(),
                    'action': 'CREATE',
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'user_id': 'system',
                    'details': {'message': 'Entity created'},
                    'level': 'INFO',
                    'status': 'SUCCESS'
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get audit trail: {str(e)}")
            return []
    
    def get_user_audit_trail(
        self, 
        user_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Get audit trail for specific user"""
        try:
            # TODO: Implement actual database query
            # For now, return placeholder data
            return [
                {
                    'timestamp': timezone.now().isoformat(),
                    'action': 'LOGIN',
                    'entity_type': 'USER',
                    'entity_id': user_id,
                    'user_id': user_id,
                    'details': {'message': 'User logged in'},
                    'level': 'INFO',
                    'status': 'SUCCESS'
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user audit trail: {str(e)}")
            return []
    
    def get_audit_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Get audit summary for date range"""
        try:
            # TODO: Implement actual database query
            # For now, return placeholder data
            return {
                'period': f"{start_date} to {end_date}",
                'total_events': 100,
                'action_breakdown': {
                    'CREATE': 25,
                    'UPDATE': 30,
                    'DELETE': 5,
                    'VIEW': 40
                },
                'user_breakdown': {
                    'admin': 50,
                    'user': 30,
                    'system': 20
                },
                'level_breakdown': {
                    'INFO': 80,
                    'WARNING': 15,
                    'ERROR': 5
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit summary: {str(e)}")
            return {
                'error': str(e)
            }


class AuditExporter(IAuditExporter):
    """Handles audit export operations"""
    
    def export_audit_trail(
        self, 
        start_date: date, 
        end_date: date, 
        format_type: str
    ) -> str:
        """Export audit trail to specified format"""
        try:
            if format_type == 'CSV':
                return self._export_to_csv(start_date, end_date)
            elif format_type == 'JSON':
                return self._export_to_json(start_date, end_date)
            else:
                return f"Export format {format_type} not supported"
                
        except Exception as e:
            logger.error(f"Failed to export audit trail: {str(e)}")
            return f"Export failed: {str(e)}"
    
    def _export_to_csv(self, start_date: date, end_date: date) -> str:
        """Export audit trail to CSV"""
        # TODO: Implement actual CSV export
        return f"CSV export for {start_date} to {end_date} (placeholder)"
    
    def _export_to_json(self, start_date: date, end_date: date) -> str:
        """Export audit trail to JSON"""
        # TODO: Implement actual JSON export
        return f"JSON export for {start_date} to {end_date} (placeholder)"


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class AuditTrailService:
    """
    Composes audit trail and logging functionality
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        logger: IAuditLogger,
        query: IAuditQuery,
        exporter: IAuditExporter
    ):
        self.logger = logger
        self.query = query
        self.exporter = exporter
    
    def log_claim_creation(self, claim_id: str, user_id: str, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log claim creation"""
        return self.logger.log_audit_event(
            action=AuditAction.CREATE,
            entity_type='CLAIM',
            entity_id=claim_id,
            user_id=user_id,
            details={
                'claim_number': claim_data.get('claimform_number'),
                'amount': str(claim_data.get('hospital_claimamount')),
                'hospital': claim_data.get('hospital_name'),
                'member': claim_data.get('member_name')
            }
        )
    
    def log_claim_approval(self, claim_id: str, user_id: str, approver_id: str) -> Dict[str, Any]:
        """Log claim approval"""
        return self.logger.log_audit_event(
            action=AuditAction.APPROVE,
            entity_type='CLAIM',
            entity_id=claim_id,
            user_id=user_id,
            details={
                'approver_id': approver_id,
                'approval_date': timezone.now().isoformat()
            }
        )
    
    def log_claim_rejection(self, claim_id: str, user_id: str, reason: str) -> Dict[str, Any]:
        """Log claim rejection"""
        return self.logger.log_audit_event(
            action=AuditAction.REJECT,
            entity_type='CLAIM',
            entity_id=claim_id,
            user_id=user_id,
            details={
                'rejection_reason': reason,
                'rejection_date': timezone.now().isoformat()
            }
        )
    
    def log_member_creation(self, member_id: str, user_id: str, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log member creation"""
        return self.logger.log_audit_event(
            action=AuditAction.CREATE,
            entity_type='MEMBER',
            entity_id=member_id,
            user_id=user_id,
            details={
                'member_name': member_data.get('member_name'),
                'employee_id': member_data.get('employee_id'),
                'scheme': member_data.get('scheme_name')
            }
        )
    
    def log_provider_registration(self, provider_id: str, user_id: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log provider registration"""
        return self.logger.log_audit_event(
            action=AuditAction.CREATE,
            entity_type='PROVIDER',
            entity_id=provider_id,
            user_id=user_id,
            details={
                'hospital_name': provider_data.get('hospital_name'),
                'hospital_reference': provider_data.get('hospital_reference'),
                'contact_person': provider_data.get('contact_person')
            }
        )
    
    def log_user_login(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Log user login"""
        return self.logger.log_audit_event(
            action=AuditAction.LOGIN,
            entity_type='USER',
            entity_id=user_id,
            user_id=user_id,
            details={
                'ip_address': ip_address,
                'login_time': timezone.now().isoformat()
            }
        )
    
    def log_user_logout(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Log user logout"""
        return self.logger.log_audit_event(
            action=AuditAction.LOGOUT,
            entity_type='USER',
            entity_id=user_id,
            user_id=user_id,
            details={
                'ip_address': ip_address,
                'logout_time': timezone.now().isoformat()
            }
        )
    
    def log_security_violation(self, user_id: str, violation_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Log security violation"""
        return self.logger.log_security_event(
            event_type=violation_type,
            user_id=user_id,
            details=details
        )
    
    def get_entity_audit_trail(self, entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for specific entity"""
        return self.query.get_audit_trail(entity_type, entity_id)
    
    def get_user_audit_trail(self, user_id: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get audit trail for specific user"""
        return self.query.get_user_audit_trail(user_id, start_date, end_date)
    
    def get_audit_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get audit summary for date range"""
        return self.query.get_audit_summary(start_date, end_date)
    
    def export_audit_trail(self, start_date: date, end_date: date, format_type: str) -> str:
        """Export audit trail"""
        return self.exporter.export_audit_trail(start_date, end_date, format_type)


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class AuditTrailFactory:
    """Factory for creating audit trail instances"""
    
    @staticmethod
    def create_audit_trail_service() -> AuditTrailService:
        """Create configured audit trail service"""
        logger = AuditLogger()
        query = AuditQuery()
        exporter = AuditExporter()
        
        return AuditTrailService(logger, query, exporter)
