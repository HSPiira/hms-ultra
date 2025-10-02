"""
Member Lifecycle Management
Implements SOLID principles for member status management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from django.db import transaction
from django.utils import timezone

from .models import Member, Scheme, MemberDependant


class MemberStatus(Enum):
    """Member status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TERMINATED = "TERMINATED"
    SUSPENDED = "SUSPENDED"


class MemberAction(Enum):
    """Member action enumeration"""
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"
    RENEW = "RENEW"
    TERMINATE = "TERMINATE"
    SUSPEND = "SUSPEND"
    CHANGE_CATEGORY = "CHANGE_CATEGORY"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IMemberValidator(ABC):
    """Interface for member validation rules"""
    
    @abstractmethod
    def validate_member_data(self, member_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def validate_scheme_eligibility(self, member_id: str, scheme_id: str) -> bool:
        pass


class IMemberStatusManager(ABC):
    """Interface for member status management"""
    
    @abstractmethod
    def can_activate_member(self, member_id: str) -> bool:
        pass
    
    @abstractmethod
    def can_deactivate_member(self, member_id: str) -> bool:
        pass
    
    @abstractmethod
    def can_renew_member(self, member_id: str) -> bool:
        pass


class IMemberLifecycleProcessor(ABC):
    """Interface for member lifecycle processing"""
    
    @abstractmethod
    def process_member_action(
        self, 
        member_id: str, 
        action: MemberAction, 
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class MemberValidator(IMemberValidator):
    """Validates member data and eligibility"""
    
    def validate_member_data(self, member_data: Dict[str, Any]) -> bool:
        """Validate member data completeness and format"""
        required_fields = [
            'member_name', 'date_of_birth', 'gender', 
            'phone_home', 'postal_address'
        ]
        
        for field in required_fields:
            if not member_data.get(field):
                return False
        
        # Validate date of birth
        dob = member_data.get('date_of_birth')
        if dob and isinstance(dob, str):
            try:
                datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                return False
        
        return True
    
    def validate_scheme_eligibility(self, member_id: str, scheme_id: str) -> bool:
        """Validate if member is eligible for scheme"""
        try:
            member = Member.objects.get(id=member_id)
            scheme = Scheme.objects.get(id=scheme_id)
            
            # Check if member is active
            if member.member_status != 'ACTIVE':
                return False
            
            # Check if scheme is not terminated
            if scheme.termination == 'YES':
                return False
            
            # Check if member's company matches scheme's company
            if member.company_id != scheme.company_id:
                return False
            
            return True
            
        except (Member.DoesNotExist, Scheme.DoesNotExist):
            return False


class MemberStatusManager(IMemberStatusManager):
    """Manages member status transitions"""
    
    def can_activate_member(self, member_id: str) -> bool:
        """Check if member can be activated"""
        try:
            member = Member.objects.get(id=member_id)
            
            # Can only activate inactive members
            if member.member_status not in ['INACTIVE', 'SUSPENDED']:
                return False
            
            # Check if member has valid scheme
            if not member.scheme or member.scheme.termination == 'YES':
                return False
            
            return True
            
        except Member.DoesNotExist:
            return False
    
    def can_deactivate_member(self, member_id: str) -> bool:
        """Check if member can be deactivated"""
        try:
            member = Member.objects.get(id=member_id)
            
            # Can only deactivate active members
            if member.member_status != 'ACTIVE':
                return False
            
            return True
            
        except Member.DoesNotExist:
            return False
    
    def can_renew_member(self, member_id: str) -> bool:
        """Check if member can be renewed"""
        try:
            member = Member.objects.get(id=member_id)
            
            # Can renew active or inactive members
            if member.member_status not in ['ACTIVE', 'INACTIVE']:
                return False
            
            # Check if member has valid scheme
            if not member.scheme or member.scheme.termination == 'YES':
                return False
            
            return True
            
        except Member.DoesNotExist:
            return False


class MemberLifecycleProcessor(IMemberLifecycleProcessor):
    """Processes member lifecycle actions"""
    
    def __init__(
        self, 
        validator: IMemberValidator, 
        status_manager: IMemberStatusManager
    ):
        self.validator = validator
        self.status_manager = status_manager
    
    @transaction.atomic
    def process_member_action(
        self, 
        member_id: str, 
        action: MemberAction, 
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process member lifecycle action"""
        try:
            member = Member.objects.get(id=member_id)
            
            if action == MemberAction.ACTIVATE:
                return self._activate_member(member, action_data)
            elif action == MemberAction.DEACTIVATE:
                return self._deactivate_member(member, action_data)
            elif action == MemberAction.RENEW:
                return self._renew_member(member, action_data)
            elif action == MemberAction.TERMINATE:
                return self._terminate_member(member, action_data)
            elif action == MemberAction.SUSPEND:
                return self._suspend_member(member, action_data)
            elif action == MemberAction.CHANGE_CATEGORY:
                return self._change_member_category(member, action_data)
            else:
                return {'success': False, 'message': 'Invalid action'}
                
        except Member.DoesNotExist:
            return {'success': False, 'message': 'Member not found'}
    
    def _activate_member(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Activate member"""
        if not self.status_manager.can_activate_member(member.id):
            return {'success': False, 'message': 'Member cannot be activated'}
        
        member.member_status = 'ACTIVE'
        member.date_of_joining = action_data.get('start_date', timezone.now().date())
        member.save()
        
        return {
            'success': True, 
            'message': 'Member activated successfully',
            'member_status': member.member_status
        }
    
    def _deactivate_member(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deactivate member"""
        if not self.status_manager.can_deactivate_member(member.id):
            return {'success': False, 'message': 'Member cannot be deactivated'}
        
        member.member_status = 'INACTIVE'
        member.date_of_leaving = action_data.get('end_date', timezone.now().date())
        member.save()
        
        return {
            'success': True, 
            'message': 'Member deactivated successfully',
            'member_status': member.member_status
        }
    
    def _renew_member(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Renew member membership"""
        if not self.status_manager.can_renew_member(member.id):
            return {'success': False, 'message': 'Member cannot be renewed'}
        
        # Update membership dates
        member.date_of_joining = action_data.get('start_date', timezone.now().date())
        member.date_of_leaving = action_data.get('end_date')
        member.member_status = 'ACTIVE'
        member.save()
        
        return {
            'success': True, 
            'message': 'Member renewed successfully',
            'member_status': member.member_status
        }
    
    def _terminate_member(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate member membership"""
        member.member_status = 'TERMINATED'
        member.date_of_leaving = action_data.get('end_date', timezone.now().date())
        member.save()
        
        return {
            'success': True, 
            'message': 'Member terminated successfully',
            'member_status': member.member_status
        }
    
    def _suspend_member(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suspend member membership"""
        if member.member_status != 'ACTIVE':
            return {'success': False, 'message': 'Only active members can be suspended'}
        
        member.member_status = 'SUSPENDED'
        member.save()
        
        return {
            'success': True, 
            'message': 'Member suspended successfully',
            'member_status': member.member_status
        }
    
    def _change_member_category(self, member: Member, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Change member category/grade"""
        new_category = action_data.get('new_category')
        if not new_category:
            return {'success': False, 'message': 'New category is required'}
        
        # Update member category
        member.category = new_category
        member.save()
        
        return {
            'success': True, 
            'message': 'Member category changed successfully',
            'new_category': new_category
        }


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class MemberLifecycleService:
    """
    Composes member lifecycle management
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        validator: IMemberValidator,
        status_manager: IMemberStatusManager,
        processor: IMemberLifecycleProcessor
    ):
        self.validator = validator
        self.status_manager = status_manager
        self.processor = processor
    
    def activate_member(
        self, 
        member_id: str, 
        start_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Activate member with business rules"""
        action_data = {
            'start_date': start_date,
            'reason': reason
        }
        return self.processor.process_member_action(
            member_id, MemberAction.ACTIVATE, action_data
        )
    
    def deactivate_member(
        self, 
        member_id: str, 
        end_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Deactivate member with business rules"""
        action_data = {
            'end_date': end_date,
            'reason': reason
        }
        return self.processor.process_member_action(
            member_id, MemberAction.DEACTIVATE, action_data
        )
    
    def renew_member(
        self, 
        member_id: str, 
        start_date: date, 
        end_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Renew member membership"""
        action_data = {
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason
        }
        return self.processor.process_member_action(
            member_id, MemberAction.RENEW, action_data
        )
    
    def change_member_category(
        self, 
        member_id: str, 
        new_category: str, 
        effective_date: date
    ) -> Dict[str, Any]:
        """Change member category"""
        action_data = {
            'new_category': new_category,
            'effective_date': effective_date
        }
        return self.processor.process_member_action(
            member_id, MemberAction.CHANGE_CATEGORY, action_data
        )


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class MemberLifecycleFactory:
    """Factory for creating member lifecycle instances"""
    
    @staticmethod
    def create_member_lifecycle_service() -> MemberLifecycleService:
        """Create configured member lifecycle service"""
        validator = MemberValidator()
        status_manager = MemberStatusManager()
        processor = MemberLifecycleProcessor(validator, status_manager)
        
        return MemberLifecycleService(validator, status_manager, processor)
