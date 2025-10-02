"""
Complete Claim Workflow Management
Implements SOLID principles for end-to-end claim processing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from django.db import transaction, models, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Claim, Member, Hospital, Scheme, ClaimDetail, ClaimPayment
from .business_logic_service import get_business_logic_service
from .smart_api_service import SmartAPIServiceFactory


class ClaimWorkflowStatus(Enum):
    """
    Claim workflow status enumeration.
    
    Defines all possible states a claim can be in during its lifecycle.
    Used to track the progress of claims through the approval process.
    """
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"
    REVERTED = "REVERTED"
    QUARANTINED = "QUARANTINED"


class ClaimWorkflowStage(Enum):
    """
    Claim workflow stage enumeration.
    
    Defines the different stages a claim goes through during processing.
    Used to organize the workflow and determine next steps.
    """
    INITIAL_SUBMISSION = "INITIAL_SUBMISSION"
    DATA_VALIDATION = "DATA_VALIDATION"
    BUSINESS_RULE_VALIDATION = "BUSINESS_RULE_VALIDATION"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    APPROVAL = "APPROVAL"
    PAYMENT_PROCESSING = "PAYMENT_PROCESSING"
    COMPLETION = "COMPLETION"


class ClaimWorkflowAction(Enum):
    """Claim workflow action enumeration"""
    SUBMIT = "SUBMIT"
    VALIDATE = "VALIDATE"
    REVIEW = "REVIEW"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PAY = "PAY"
    REVERT = "REVERT"
    QUARANTINE = "QUARANTINE"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IClaimWorkflowValidator(ABC):
    """Interface for claim workflow validation"""
    
    @abstractmethod
    def validate_claim_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_claim_eligibility(self, claim_id: str) -> Dict[str, Any]:
        pass


class IClaimWorkflowProcessor(ABC):
    """Interface for claim workflow processing"""
    
    @abstractmethod
    def process_claim_submission(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_claim_approval(self, claim_id: str, approver_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_claim_rejection(self, claim_id: str, reason: str, rejector_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_claim_payment(self, claim_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class IClaimWorkflowNotifier(ABC):
    """Interface for claim workflow notifications"""
    
    @abstractmethod
    def notify_claim_submitted(self, claim_id: str) -> None:
        pass
    
    @abstractmethod
    def notify_claim_approved(self, claim_id: str) -> None:
        pass
    
    @abstractmethod
    def notify_claim_rejected(self, claim_id: str, reason: str) -> None:
        pass
    
    @abstractmethod
    def notify_claim_paid(self, claim_id: str) -> None:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class ClaimWorkflowValidator(IClaimWorkflowValidator):
    """Validates claims at different workflow stages"""
    
    def __init__(self):
        self.business_service = get_business_logic_service()
    
    def validate_claim_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim data completeness and format"""
        required_fields = [
            'member_id', 'hospital_id', 'service_date', 
            'claimform_number', 'invoice_number', 'hospital_claimamount'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not claim_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'errors': [f'Missing required field: {field}' for field in missing_fields]
            }
        
        # Validate service date
        service_date = claim_data.get('service_date')
        if isinstance(service_date, str):
            try:
                service_date = datetime.strptime(service_date, '%Y-%m-%d').date()
            except ValueError:
                return {
                    'valid': False,
                    'errors': ['Invalid service date format']
                }
        
        # Validate amount
        amount = claim_data.get('hospital_claimamount')
        if amount is None or amount <= 0:
            return {
                'valid': False,
                'errors': ['Hospital claim amount must be greater than zero']
            }
        
        return {'valid': True, 'errors': []}
    
    def validate_claim_eligibility(self, claim_id: str) -> Dict[str, Any]:
        """Validate claim eligibility using business rules"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            # Prepare claim data for business rule validation
            claim_data = {
                'member_id': str(claim.member_id),
                'scheme_id': str(claim.member.scheme_id),
                'hospital_id': str(claim.hospital_id),
                'service_date': claim.service_date,
                'claimform_number': claim.claimform_number,
                'invoice_number': claim.invoice_number,
                'amount': claim.hospital_claimamount,
                'benefit_code': 'GENERAL'  # Default benefit code
            }
            
            # Use business logic service for validation
            result = self.business_service.validate_claim_eligibility(claim_data)
            
            return {
                'valid': result['success'],
                'errors': result.get('errors', []) if not result['success'] else []
            }
            
        except Claim.DoesNotExist:
            return {
                'valid': False,
                'errors': ['Claim not found']
            }


class ClaimWorkflowProcessor(IClaimWorkflowProcessor):
    """Processes claims through workflow stages"""
    
    def __init__(self, validator: IClaimWorkflowValidator, notifier: IClaimWorkflowNotifier):
        self.validator = validator
        self.notifier = notifier
        self.business_service = get_business_logic_service()
    
    @transaction.atomic
    def process_claim_submission(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process initial claim submission"""
        try:
            # Validate claim data
            validation_result = self.validator.validate_claim_data(claim_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors'],
                    'stage': ClaimWorkflowStage.INITIAL_SUBMISSION.value
                }
            
            # Create claim record
            claim = Claim.objects.create(
                member_id=claim_data['member_id'],
                hospital_id=claim_data['hospital_id'],
                service_date=claim_data['service_date'],
                claimform_number=claim_data['claimform_number'],
                invoice_number=claim_data['invoice_number'],
                hospital_claimamount=claim_data['hospital_claimamount'],
                # Status is determined by approved field (0 = submitted, 1 = approved)
                created_by=claim_data.get('created_by', 'system')
            )
            
            # Calculate financials using business logic
            financials = self.business_service.calculate_claim_financials({
                'amount': claim.hospital_claimamount,
                'scheme_id': str(claim.member.scheme_id),
                'benefit_code': 'GENERAL',
                'member_id': str(claim.member_id),
                'service_date': claim.service_date
            })
            
            # Update claim with calculated amounts
            claim.member_claimamount = financials['benefit_amount']
            claim.save()
            
            # Notify stakeholders
            self.notifier.notify_claim_submitted(str(claim.id))
            
            return {
                'success': True,
                'claim_id': str(claim.id),
                'stage': ClaimWorkflowStage.DATA_VALIDATION.value,
                'financials': financials
            }
            
        except (ValueError, IntegrityError, ValidationError, AttributeError) as e:
            return {
                'success': False,
                'error': str(e),
                'stage': ClaimWorkflowStage.INITIAL_SUBMISSION.value
            }
    
    @transaction.atomic
    def process_claim_approval(self, claim_id: str, approver_id: str) -> Dict[str, Any]:
        """Process claim approval"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            # Validate claim is in correct status (using existing approved field)
            if claim.approved == 1:
                return {
                    'success': False,
                    'error': 'Claim is already approved'
                }
            
            # Update claim status using existing fields
            claim.approved = 1  # Use existing approved field
            # Store approver info in claimformcomments field (existing field)
            claim.claimformcomments = f"Approved by {approver_id} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            claim.save()
            
            # Notify stakeholders
            self.notifier.notify_claim_approved(claim_id)
            
            return {
                'success': True,
                'claim_id': claim_id,
                'stage': ClaimWorkflowStage.APPROVAL.value,
                'approved_by': approver_id
            }
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }
    
    @transaction.atomic
    def process_claim_rejection(self, claim_id: str, reason: str, rejector_id: str) -> Dict[str, Any]:
        """Process claim rejection"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            # Update claim status using existing fields
            # Store rejection info in claimformcomments field
            claim.claimformcomments = f"Rejected by {rejector_id} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}: {reason}"
            claim.save()
            
            # Notify stakeholders
            self.notifier.notify_claim_rejected(claim_id, reason)
            
            return {
                'success': True,
                'claim_id': claim_id,
                'stage': ClaimWorkflowStage.APPROVAL.value,
                'rejected_by': rejector_id,
                'reason': reason
            }
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }
    
    @transaction.atomic
    def process_claim_payment(self, claim_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process claim payment"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            # Validate claim is approved using existing approved field
            if claim.approved != 1:
                return {
                    'success': False,
                    'error': f'Claim must be approved to process payment. Current status: {"SUBMITTED" if claim.approved == 0 else "UNKNOWN"}'
                }
            
            # Process payment using business logic
            payment_result = self.business_service.process_claim_payment(
                claim_id, 
                payment_data.get('amount', claim.member_claimamount)
            )
            
            if not payment_result['success']:
                return payment_result
            
            # Update claim status using existing fields
            # Store payment info in claimformcomments field
            claim.claimformcomments = f"{claim.claimformcomments} | Paid on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            claim.save()
            
            # Notify stakeholders
            self.notifier.notify_claim_paid(claim_id)
            
            return {
                'success': True,
                'claim_id': claim_id,
                'stage': ClaimWorkflowStage.PAYMENT_PROCESSING.value,
                'payment_id': payment_result.get('payment_id'),
                'amount': payment_result.get('payment_amount')
            }
            
        except Claim.DoesNotExist:
            return {
                'success': False,
                'error': 'Claim not found'
            }


class ClaimWorkflowNotifier(IClaimWorkflowNotifier):
    """Handles claim workflow notifications"""
    
    def notify_claim_submitted(self, claim_id: str) -> None:
        """Notify stakeholders of claim submission"""
        # TODO: Implement actual notification logic
        # This could include email, SMS, in-app notifications, etc.
        print(f"Notification: Claim {claim_id} has been submitted")
    
    def notify_claim_approved(self, claim_id: str) -> None:
        """Notify stakeholders of claim approval"""
        # TODO: Implement actual notification logic
        print(f"Notification: Claim {claim_id} has been approved")
    
    def notify_claim_rejected(self, claim_id: str, reason: str) -> None:
        """Notify stakeholders of claim rejection"""
        # TODO: Implement actual notification logic
        print(f"Notification: Claim {claim_id} has been rejected. Reason: {reason}")
    
    def notify_claim_paid(self, claim_id: str) -> None:
        """Notify stakeholders of claim payment"""
        # TODO: Implement actual notification logic
        print(f"Notification: Claim {claim_id} has been paid")


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class ClaimWorkflowService:
    """
    Composes claim workflow management
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        validator: IClaimWorkflowValidator,
        processor: IClaimWorkflowProcessor,
        notifier: IClaimWorkflowNotifier
    ):
        self.validator = validator
        self.processor = processor
        self.notifier = notifier
    
    def submit_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit new claim for processing"""
        return self.processor.process_claim_submission(claim_data)
    
    def approve_claim(self, claim_id: str, approver_id: str) -> Dict[str, Any]:
        """Approve claim"""
        return self.processor.process_claim_approval(claim_id, approver_id)
    
    def reject_claim(self, claim_id: str, reason: str, rejector_id: str) -> Dict[str, Any]:
        """Reject claim"""
        return self.processor.process_claim_rejection(claim_id, reason, rejector_id)
    
    def pay_claim(self, claim_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process claim payment"""
        return self.processor.process_claim_payment(claim_id, payment_data)
    
    def get_claim_workflow_status(self, claim_id: str) -> Dict[str, Any]:
        """Get current workflow status of claim"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            return {
                'claim_id': claim_id,
                'status': 'APPROVED' if claim.approved == 1 else 'SUBMITTED',
                'stage': self._determine_workflow_stage(claim),
                'submitted_date': claim.created_at,  # Use existing created_at field
                'approved_date': claim.claimformcomments if claim.approved == 1 else None,  # Extract from comments
                'paid_date': None,  # TODO: Add payment tracking field
                'amount': claim.hospital_claimamount,
                'benefit_amount': claim.member_claimamount
            }
            
        except Claim.DoesNotExist:
            return {
                'error': 'Claim not found'
            }
    
    def _determine_workflow_stage(self, claim: Claim) -> str:
        """Determine current workflow stage based on claim status"""
        # Use existing approved field to determine stage
        if claim.approved == 1:
            return ClaimWorkflowStage.APPROVAL.value
        else:
            return ClaimWorkflowStage.DATA_VALIDATION.value


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class ClaimWorkflowFactory:
    """Factory for creating claim workflow instances"""
    
    @staticmethod
    def create_claim_workflow_service() -> ClaimWorkflowService:
        """Create configured claim workflow service"""
        validator = ClaimWorkflowValidator()
        notifier = ClaimWorkflowNotifier()
        processor = ClaimWorkflowProcessor(validator, notifier)
        
        return ClaimWorkflowService(validator, processor, notifier)
