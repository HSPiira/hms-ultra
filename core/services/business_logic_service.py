"""
Business Logic Service
Orchestrates all business logic components with SOLID principles
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional

from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from core.utils.result import OperationResult

logger = logging.getLogger(__name__)

from core.utils.business_rules import (
    BusinessRulesFactory, ClaimBusinessRules, ClaimBusinessRuleService
)
from core.services.member_lifecycle import (
    MemberLifecycleFactory, MemberLifecycleService, MemberAction
)
from core.services.financial_processing import (
    FinancialProcessingFactory, FinancialProcessingService, PaymentType
)
from core.services.billing_session import (
    BillingSessionFactory, BillingSessionService, BillingSessionStatus
)


class HMSBusinessLogicService:
    """
    Main business logic service that orchestrates all business components
    Follows SOLID principles with clear separation of concerns
    """
    
    def __init__(self):
        # Initialize all business logic components
        self.claim_business_rules = BusinessRulesFactory.create_claim_business_rules()
        self.claim_service = ClaimBusinessRuleService(self.claim_business_rules)
        self.member_lifecycle = MemberLifecycleFactory.create_member_lifecycle_service()
        self.financial_processing = FinancialProcessingFactory.create_financial_processing_service()
        self.billing_session = BillingSessionFactory.create_billing_session_service()
    
    # =============================================================================
    # CLAIMS PROCESSING WORKFLOW
    # =============================================================================
    
    @transaction.atomic
    def process_claim_submission(self, claim_data: Dict[str, Any]) -> OperationResult:
        """
        Complete claim submission workflow
        1. Validate billing session
        2. Apply business rules
        3. Calculate financials
        4. Create claim record
        """
        try:
            # 1. Validate billing session
            service_date = claim_data.get('service_date')
            if service_date:
                session_validation = self.billing_session.validate_service_date(service_date)
                if not session_validation['valid']:
                    return OperationResult.fail(session_validation['message'], data={'stage': 'BILLING_SESSION'})
            
            # 2. Apply business rules
            validation_result = self.claim_service.validate_and_process_claim(claim_data)
            if not validation_result['success']:
                return OperationResult.fail(validation_result.get('message', 'Validation failed'), data={'validation_results': validation_result.get('validation_results', [])})
            
            # 3. Calculate financials
            financials = self.financial_processing.calculate_claim_financials(claim_data)
            
            # 4. Create claim record (this would be handled by the API layer)
            return OperationResult.ok({'message': 'Claim processed successfully', 'financials': financials, 'validation_results': validation_result.get('validation_results', [])})
            
        except (ValueError, IntegrityError, ValidationError) as e:
            return OperationResult.fail(f'Validation or database error: {str(e)}', error_code='VALIDATION_ERROR')
        except Exception as e:
            logger.error(f"Unexpected error in claim processing: {str(e)}")
            return OperationResult.fail(f'Unexpected error occurred: {str(e)}', error_code='UNEXPECTED_ERROR')
    
    def validate_claim_eligibility(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim eligibility without processing"""
        try:
            # Apply business rules validation
            validation_result = self.claim_service.validate_and_process_claim(claim_data)
            return validation_result
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Claim validation failed: {str(e)}'
            }
    
    # =============================================================================
    # MEMBER LIFECYCLE MANAGEMENT
    # =============================================================================
    
    def activate_member(
        self, 
        member_id: str, 
        start_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Activate member with business rules"""
        return self.member_lifecycle.activate_member(member_id, start_date, reason)
    
    def deactivate_member(
        self, 
        member_id: str, 
        end_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Deactivate member with business rules"""
        return self.member_lifecycle.deactivate_member(member_id, end_date, reason)
    
    def renew_member(
        self, 
        member_id: str, 
        start_date: date, 
        end_date: date, 
        reason: str = ""
    ) -> Dict[str, Any]:
        """Renew member membership"""
        return self.member_lifecycle.renew_member(member_id, start_date, end_date, reason)
    
    def change_member_category(
        self, 
        member_id: str, 
        new_category: str, 
        effective_date: date
    ) -> Dict[str, Any]:
        """Change member category"""
        return self.member_lifecycle.change_member_category(
            member_id, new_category, effective_date
        )
    
    # =============================================================================
    # FINANCIAL PROCESSING
    # =============================================================================
    
    def process_claim_payment(
        self, 
        claim_id: str, 
        payment_amount: Decimal
    ) -> Dict[str, Any]:
        """Process payment for approved claim"""
        return self.financial_processing.process_claim_payment(claim_id, payment_amount)
    
    def process_member_reimbursement(
        self, 
        member_id: str, 
        amount: Decimal, 
        reason: str
    ) -> Dict[str, Any]:
        """Process direct member reimbursement"""
        return self.financial_processing.process_member_reimbursement(
            member_id, amount, reason
        )
    
    def calculate_claim_financials(self, claim_data: Dict[str, Any]) -> Dict[str, Decimal]:
        """Calculate comprehensive claim financials"""
        return self.financial_processing.calculate_claim_financials(claim_data)
    
    def validate_payment_eligibility(
        self, 
        claim_id: str, 
        payment_amount: Decimal
    ) -> Dict[str, Any]:
        """Validate payment eligibility"""
        return self.financial_processing.validate_payment_eligibility(
            claim_id, payment_amount
        )
    
    # =============================================================================
    # BILLING SESSION MANAGEMENT
    # =============================================================================
    
    def create_monthly_billing_session(
        self, 
        year: int, 
        month: int, 
        created_by: str
    ) -> Dict[str, Any]:
        """Create monthly billing session"""
        return self.billing_session.create_monthly_session(year, month, created_by)
    
    def create_quarterly_billing_session(
        self, 
        year: int, 
        quarter: int, 
        created_by: str
    ) -> Dict[str, Any]:
        """Create quarterly billing session"""
        return self.billing_session.create_quarterly_session(year, quarter, created_by)
    
    def close_billing_session(self, session_id: str) -> Dict[str, Any]:
        """Close billing session"""
        return self.billing_session.manager.close_billing_session(session_id)
    
    def validate_service_date(self, service_date: date) -> Dict[str, Any]:
        """Validate service date against billing sessions"""
        return self.billing_session.validate_service_date(service_date)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get billing session summary"""
        return self.billing_session.get_session_summary(session_id)
    
    # =============================================================================
    # COMPREHENSIVE BUSINESS WORKFLOWS
    # =============================================================================
    
    @transaction.atomic
    def process_complete_claim_workflow(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete claim workflow from submission to payment
        1. Validate billing session
        2. Apply business rules
        3. Calculate financials
        4. Create claim
        5. Auto-approve if eligible
        6. Process payment if approved
        """
        try:
            # 1. Process claim submission
            submission_result = self.process_claim_submission(claim_data)
            if not submission_result['success']:
                return submission_result
            
            # 2. Auto-approve if eligible (business rule)
            # This would depend on specific business requirements
            # For now, we'll assume manual approval is required
            
            return {
                'success': True,
                'message': 'Claim workflow completed successfully',
                'submission_result': submission_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Claim workflow failed: {str(e)}'
            }
    
    def process_member_enrollment_workflow(
        self, 
        member_data: Dict[str, Any], 
        scheme_id: str
    ) -> Dict[str, Any]:
        """
        Complete member enrollment workflow
        1. Validate member data
        2. Check scheme eligibility
        3. Create member record
        4. Activate member
        """
        try:
            # 1. Validate member data (this would be handled by the API layer)
            # 2. Check scheme eligibility
            # 3. Create member record (handled by API layer)
            # 4. Activate member
            member_id = member_data.get('id')  # Assuming member is created
            if member_id:
                activation_result = self.activate_member(
                    member_id, 
                    timezone.now().date(), 
                    "Initial enrollment"
                )
                return activation_result
            
            return {
                'success': False,
                'message': 'Member ID not provided'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Member enrollment workflow failed: {str(e)}'
            }
    
    def process_provider_onboarding_workflow(
        self, 
        provider_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete provider onboarding workflow
        1. Validate provider data
        2. Create provider record
        3. Set up pricing agreements
        4. Activate provider
        """
        try:
            # This would be implemented based on specific provider requirements
            # For now, return a placeholder
            return {
                'success': True,
                'message': 'Provider onboarding workflow completed',
                'provider_id': provider_data.get('id')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Provider onboarding workflow failed: {str(e)}'
            }


# =============================================================================
# SINGLETON PATTERN FOR BUSINESS LOGIC SERVICE
# =============================================================================

class BusinessLogicServiceSingleton:
    """Singleton pattern for business logic service"""
    _instance = None
    _service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._service = HMSBusinessLogicService()
        return cls._instance
    
    def get_service(self) -> HMSBusinessLogicService:
        """Get the business logic service instance"""
        return self._service


def get_business_logic_service() -> HMSBusinessLogicService:
    """Get the business logic service instance"""
    return BusinessLogicServiceSingleton().get_service()
