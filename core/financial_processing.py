"""
Financial Processing Logic
Implements SOLID principles for financial calculations and processing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from django.db import transaction, models
from django.utils import timezone

from .models import (
    Claim, Member, Scheme, Benefit, SchemeBenefit, 
    ClaimPayment, BillingSession, FinancialPeriod
)


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentType(Enum):
    """Payment type enumeration"""
    CLAIM_PAYMENT = "CLAIM_PAYMENT"
    REIMBURSEMENT = "REIMBURSEMENT"
    REFUND = "REFUND"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class ICoPaymentCalculator(ABC):
    """Interface for co-payment calculations"""
    
    @abstractmethod
    def calculate_co_payment(
        self, 
        claim_amount: Decimal, 
        member_scheme: str, 
        benefit_code: str
    ) -> Decimal:
        pass


class IBenefitLimitCalculator(ABC):
    """Interface for benefit limit calculations"""
    
    @abstractmethod
    def calculate_remaining_benefit(
        self, 
        member_id: str, 
        benefit_code: str, 
        service_date: date
    ) -> Decimal:
        pass
    
    @abstractmethod
    def calculate_used_benefit(
        self, 
        member_id: str, 
        benefit_code: str, 
        period_start: date, 
        period_end: date
    ) -> Decimal:
        pass


class IPaymentProcessor(ABC):
    """Interface for payment processing"""
    
    @abstractmethod
    def process_payment(
        self, 
        claim_id: str, 
        payment_amount: Decimal, 
        payment_type: PaymentType
    ) -> Dict[str, Any]:
        pass


class IReimbursementProcessor(ABC):
    """Interface for reimbursement processing"""
    
    @abstractmethod
    def process_reimbursement(
        self, 
        member_id: str, 
        amount: Decimal, 
        reason: str
    ) -> Dict[str, Any]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class CoPaymentCalculator(ICoPaymentCalculator):
    """Calculates member co-payments"""
    
    def calculate_co_payment(
        self, 
        claim_amount: Decimal, 
        member_scheme: str, 
        benefit_code: str
    ) -> Decimal:
        """Calculate member co-payment amount"""
        try:
            # Get scheme benefit
            scheme_benefit = SchemeBenefit.objects.filter(
                scheme_id=member_scheme,
                scheme_benefit__service_name=benefit_code
            ).first()
            
            if not scheme_benefit:
                return claim_amount  # No benefit, full co-payment
            
            # Calculate co-payment percentage
            copayment_percent = scheme_benefit.copayment_percent or 0
            co_payment = claim_amount * (copayment_percent / 100)
            
            # Round to 2 decimal places
            return co_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception:
            return claim_amount  # Default to full amount on error


class BenefitLimitCalculator(IBenefitLimitCalculator):
    """Calculates benefit limits and usage"""
    
    def calculate_remaining_benefit(
        self, 
        member_id: str, 
        benefit_code: str, 
        service_date: date
    ) -> Decimal:
        """Calculate remaining benefit limit for member"""
        try:
            # Get member's scheme
            member = Member.objects.get(id=member_id)
            scheme = member.scheme
            
            # Get scheme benefit
            scheme_benefit = SchemeBenefit.objects.filter(
                scheme=scheme,
                scheme_benefit__service_name=benefit_code
            ).first()
            
            if not scheme_benefit:
                return Decimal('0')
            
            # Calculate used amount for the period
            period_start = date(service_date.year, 1, 1)  # Start of year
            period_end = date(service_date.year, 12, 31)  # End of year
            
            used_amount = self.calculate_used_benefit(
                member_id, benefit_code, period_start, period_end
            )
            
            # Calculate remaining limit
            limit_amount = scheme_benefit.limit_amount or Decimal('0')
            remaining_limit = limit_amount - used_amount
            
            return max(Decimal('0'), remaining_limit)
            
        except Exception:
            return Decimal('0')
    
    def calculate_used_benefit(
        self, 
        member_id: str, 
        benefit_code: str, 
        period_start: date, 
        period_end: date
    ) -> Decimal:
        """Calculate used benefit amount for period"""
        try:
            # Get used amount from approved/paid claims
            used_amount = Claim.objects.filter(
                member_id=member_id,
                service_date__gte=period_start,
                service_date__lte=period_end,
                transaction_status__in=['APPROVED', 'PAID']
            ).aggregate(
                total=models.Sum('member_claimamount')
            )['total'] or Decimal('0')
            
            return used_amount
            
        except Exception:
            return Decimal('0')


class PaymentProcessor(IPaymentProcessor):
    """Processes claim payments"""
    
    def process_payment(
        self, 
        claim_id: str, 
        payment_amount: Decimal, 
        payment_type: PaymentType
    ) -> Dict[str, Any]:
        """Process payment for claim"""
        try:
            with transaction.atomic():
                # Get claim
                claim = Claim.objects.get(id=claim_id)
                
                # Validate payment amount
                if payment_amount <= 0:
                    return {
                        'success': False, 
                        'message': 'Payment amount must be greater than zero'
                    }
                
            # Check if claim is approved
            if claim.transaction_status != 'APPROVED':
                return {
                    'success': False, 
                    'message': 'Claim must be approved before payment'
                }
                
                # Create payment record
                payment = ClaimPayment.objects.create(
                    claim=claim,
                    payment_amount=payment_amount,
                    payment_type=payment_type.value,
                    payment_status='PROCESSED',
                    payment_date=timezone.now().date(),
                    created_by='system'  # TODO: Get from current user
                )
                
                # Update claim status
                claim.transaction_status = 'PAID'
                claim.save()
                
                return {
                    'success': True,
                    'message': 'Payment processed successfully',
                    'payment_id': payment.id,
                    'payment_amount': payment_amount
                }
                
        except Claim.DoesNotExist:
            return {
                'success': False, 
                'message': 'Claim not found'
            }
        except Exception as e:
            return {
                'success': False, 
                'message': f'Payment processing failed: {str(e)}'
            }


class ReimbursementProcessor(IReimbursementProcessor):
    """Processes member reimbursements"""
    
    def process_reimbursement(
        self, 
        member_id: str, 
        amount: Decimal, 
        reason: str
    ) -> Dict[str, Any]:
        """Process direct member reimbursement"""
        try:
            with transaction.atomic():
                # Get member
                member = Member.objects.get(id=member_id)
                
                # Validate amount
                if amount <= 0:
                    return {
                        'success': False, 
                        'message': 'Reimbursement amount must be greater than zero'
                    }
                
                # Create reimbursement claim
                reimbursement_claim = Claim.objects.create(
                    member=member,
                    claimform_number=f"REIMB-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    service_date=timezone.now().date(),
                    hospital_claimamount=amount,
                    member_claimamount=amount,
                    transaction_status='APPROVED',  # Auto-approve reimbursements
                    created_by='system'  # TODO: Get from current user
                )
                
                # Create payment record
                payment = ClaimPayment.objects.create(
                    claim=reimbursement_claim,
                    payment_amount=amount,
                    payment_type='REIMBURSEMENT',
                    payment_status='PROCESSED',
                    payment_date=timezone.now().date(),
                    remarks=reason,
                    created_by='system'  # TODO: Get from current user
                )
                
                return {
                    'success': True,
                    'message': 'Reimbursement processed successfully',
                    'claim_id': reimbursement_claim.id,
                    'payment_id': payment.id,
                    'amount': amount
                }
                
        except Member.DoesNotExist:
            return {
                'success': False, 
                'message': 'Member not found'
            }
        except Exception as e:
            return {
                'success': False, 
                'message': f'Reimbursement processing failed: {str(e)}'
            }


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class FinancialProcessingService:
    """
    Composes financial processing logic
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        co_payment_calculator: ICoPaymentCalculator,
        benefit_limit_calculator: IBenefitLimitCalculator,
        payment_processor: IPaymentProcessor,
        reimbursement_processor: IReimbursementProcessor
    ):
        self.co_payment_calculator = co_payment_calculator
        self.benefit_limit_calculator = benefit_limit_calculator
        self.payment_processor = payment_processor
        self.reimbursement_processor = reimbursement_processor
    
    def calculate_claim_financials(
        self, 
        claim_data: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Calculate comprehensive claim financials"""
        claim_amount = Decimal(str(claim_data.get('amount', 0)))
        member_scheme = claim_data.get('scheme_id')
        benefit_code = claim_data.get('benefit_code')
        member_id = claim_data.get('member_id')
        service_date = claim_data.get('service_date')
        
        # Calculate co-payment
        co_payment = self.co_payment_calculator.calculate_co_payment(
            claim_amount, member_scheme, benefit_code
        )
        
        # Calculate benefit amount
        benefit_amount = claim_amount - co_payment
        
        # Calculate remaining benefit limit
        remaining_limit = Decimal('0')
        if member_id and benefit_code and service_date:
            remaining_limit = self.benefit_limit_calculator.calculate_remaining_benefit(
                member_id, benefit_code, service_date
            )
        
        # Check if claim exceeds remaining limit
        exceeds_limit = benefit_amount > remaining_limit
        if exceeds_limit:
            benefit_amount = remaining_limit
            co_payment = claim_amount - benefit_amount
        
        return {
            'total_amount': claim_amount,
            'co_payment': co_payment,
            'benefit_amount': benefit_amount,
            'remaining_limit': remaining_limit,
            'exceeds_limit': exceeds_limit
        }
    
    def process_claim_payment(
        self, 
        claim_id: str, 
        payment_amount: Decimal
    ) -> Dict[str, Any]:
        """Process payment for approved claim"""
        return self.payment_processor.process_payment(
            claim_id, payment_amount, PaymentType.CLAIM_PAYMENT
        )
    
    def process_member_reimbursement(
        self, 
        member_id: str, 
        amount: Decimal, 
        reason: str
    ) -> Dict[str, Any]:
        """Process direct member reimbursement"""
        return self.reimbursement_processor.process_reimbursement(
            member_id, amount, reason
        )
    
    def validate_payment_eligibility(
        self, 
        claim_id: str, 
        payment_amount: Decimal
    ) -> Dict[str, Any]:
        """Validate payment eligibility"""
        try:
            claim = Claim.objects.get(id=claim_id)
            
            # Check if claim is approved
            if claim.transaction_status != 'APPROVED':
                return {
                    'eligible': False,
                    'message': 'Claim must be approved before payment'
                }
            
            # Check if payment amount is valid
            if payment_amount <= 0:
                return {
                    'eligible': False,
                    'message': 'Payment amount must be greater than zero'
                }
            
            # Check if payment amount doesn't exceed benefit amount
            if payment_amount > claim.member_claimamount:
                return {
                    'eligible': False,
                    'message': 'Payment amount exceeds benefit amount'
                }
            
            return {
                'eligible': True,
                'message': 'Payment is eligible'
            }
            
        except Claim.DoesNotExist:
            return {
                'eligible': False,
                'message': 'Claim not found'
            }


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class FinancialProcessingFactory:
    """Factory for creating financial processing instances"""
    
    @staticmethod
    def create_financial_processing_service() -> FinancialProcessingService:
        """Create configured financial processing service"""
        return FinancialProcessingService(
            co_payment_calculator=CoPaymentCalculator(),
            benefit_limit_calculator=BenefitLimitCalculator(),
            payment_processor=PaymentProcessor(),
            reimbursement_processor=ReimbursementProcessor()
        )
