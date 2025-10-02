"""
Business Rules for HMS System
Implements SOLID principles with clear separation of concerns
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from django.db import transaction, models
from django.utils import timezone

from .models import (
    Claim, Member, Scheme, Hospital, Benefit, SchemeBenefit,
    MemberDependant, BillingSession, ClaimDetail
)


class ValidationResult:
    """Result of business rule validation"""
    def __init__(self, is_valid: bool, message: str = "", error_code: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.error_code = error_code


class ClaimStatus(Enum):
    """Claim status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVERTED = "REVERTED"
    PAID = "PAID"


class ClaimType(Enum):
    """Claim type enumeration"""
    FACILITY_CLAIM = 1
    REIMBURSEMENT = 2


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IClaimValidator(ABC):
    """Interface for claim validation rules"""
    
    @abstractmethod
    def validate(self, claim_data: Dict[str, Any]) -> ValidationResult:
        pass


class ISchemeValidator(ABC):
    """Interface for scheme validation rules"""
    
    @abstractmethod
    def validate_scheme_termination(self, scheme_id: str, service_date: date) -> ValidationResult:
        pass


class IDuplicateChecker(ABC):
    """Interface for duplicate checking rules"""
    
    @abstractmethod
    def check_duplicate_claim(self, claim_number: str) -> ValidationResult:
        pass
    
    @abstractmethod
    def check_duplicate_invoice(self, invoice_number: str, hospital_id: str) -> ValidationResult:
        pass


class IPriceValidator(ABC):
    """Interface for price validation rules"""
    
    @abstractmethod
    def validate_hospital_price_agreement(
        self, 
        hospital_id: str, 
        service_code: str, 
        amount: Decimal
    ) -> ValidationResult:
        pass


class IBenefitCalculator(ABC):
    """Interface for benefit calculation rules"""
    
    @abstractmethod
    def calculate_co_payment(
        self, 
        claim_amount: Decimal, 
        member_scheme: str, 
        benefit_code: str
    ) -> Decimal:
        pass
    
    @abstractmethod
    def calculate_benefit_limits(
        self, 
        member_id: str, 
        benefit_code: str, 
        service_date: date
    ) -> Decimal:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class SchemeTerminationValidator(ISchemeValidator):
    """Validates scheme termination status"""
    
    def validate_scheme_termination(self, scheme_id: str, service_date: date) -> ValidationResult:
        try:
            scheme = Scheme.objects.get(id=scheme_id)
            
            # Check if scheme is active (using termination field)
            if scheme.termination == 'YES':
                return ValidationResult(
                    False, 
                    "Scheme is terminated", 
                    "SCHEME_TERMINATED"
                )
            
            # Check if service date is within scheme period
            if scheme.terminationdate and service_date > scheme.terminationdate:
                return ValidationResult(
                    False, 
                    "Service date is after scheme termination date", 
                    "SCHEME_TERMINATED"
                )
            
            # Check if scheme has valid dates
            if scheme.terminationdate and scheme.terminationdate < service_date:
                return ValidationResult(
                    False, 
                    "Scheme has been terminated", 
                    "SCHEME_TERMINATED"
                )
            
            return ValidationResult(True, "Scheme is valid for service date")
            
        except Scheme.DoesNotExist:
            return ValidationResult(
                False, 
                "Scheme not found", 
                "SCHEME_NOT_FOUND"
            )


class DuplicateClaimChecker(IDuplicateChecker):
    """Checks for duplicate claims and invoices"""
    
    def check_duplicate_claim(self, claim_number: str) -> ValidationResult:
        if Claim.objects.filter(claimform_number=claim_number).exists():
            return ValidationResult(
                False, 
                "Claim number already exists in the system", 
                "DUPLICATE_CLAIM"
            )
        return ValidationResult(True, "Claim number is unique")
    
    def check_duplicate_invoice(self, invoice_number: str, hospital_id: str) -> ValidationResult:
        if Claim.objects.filter(
            invoice_number=invoice_number, 
            hospital_id=hospital_id
        ).exists():
            return ValidationResult(
                False, 
                "Invoice number already exists for this hospital", 
                "DUPLICATE_INVOICE"
            )
        return ValidationResult(True, "Invoice number is unique")


class HospitalPriceValidator(IPriceValidator):
    """Validates hospital pricing agreements"""
    
    def validate_hospital_price_agreement(
        self, 
        hospital_id: str, 
        service_code: str, 
        amount: Decimal
    ) -> ValidationResult:
        try:
            # Check if hospital exists
            hospital = Hospital.objects.get(id=hospital_id)
            
            # Check hospital service pricing
            from .models import HospitalService
            hospital_service = HospitalService.objects.filter(
                hospital_id=hospital_id,
                service__service_code=service_code
            ).first()
            
            if not hospital_service:
                return ValidationResult(
                    False, 
                    "Service not available at this hospital", 
                    "SERVICE_NOT_AVAILABLE"
                )
            
            # Check if amount is within reasonable range (within 20% of agreed price)
            agreed_price = hospital_service.amount
            if agreed_price:
                price_variance = abs(amount - agreed_price) / agreed_price
                if price_variance > 0.2:  # 20% variance
                    return ValidationResult(
                        False, 
                        f"Amount exceeds agreed price by {price_variance:.1%}", 
                        "PRICE_EXCEEDED"
                    )
            
            return ValidationResult(True, "Price is within agreement")
            
        except Hospital.DoesNotExist:
            return ValidationResult(
                False, 
                "Hospital not found", 
                "HOSPITAL_NOT_FOUND"
            )


class BenefitCalculator(IBenefitCalculator):
    """Calculates benefits and co-payments"""
    
    def calculate_co_payment(
        self, 
        claim_amount: Decimal, 
        member_scheme: str, 
        benefit_code: str
    ) -> Decimal:
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
            
            return co_payment
            
        except Exception:
            return claim_amount  # Default to full amount on error
    
    def calculate_benefit_limits(
        self, 
        member_id: str, 
        benefit_code: str, 
        service_date: date
    ) -> Decimal:
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
            used_amount = Claim.objects.filter(
                member_id=member_id,
                service_date__year=service_date.year,
                service_date__month=service_date.month,
                status__in=['APPROVED', 'PAID']
            ).aggregate(
                total=models.Sum('hospital_amount')
            )['total'] or Decimal('0')
            
            # Calculate remaining limit
            limit_amount = scheme_benefit.limit_amount or Decimal('0')
            remaining_limit = limit_amount - used_amount
            
            return max(Decimal('0'), remaining_limit)
            
        except Exception:
            return Decimal('0')


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class ClaimBusinessRules:
    """
    Composes all claim business rules
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        scheme_validator: ISchemeValidator,
        duplicate_checker: IDuplicateChecker,
        price_validator: IPriceValidator,
        benefit_calculator: IBenefitCalculator
    ):
        self.scheme_validator = scheme_validator
        self.duplicate_checker = duplicate_checker
        self.price_validator = price_validator
        self.benefit_calculator = benefit_calculator
    
    def validate_claim_submission(self, claim_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate claim submission against all business rules"""
        results = []
        
        # 1. Validate scheme termination
        scheme_id = claim_data.get('scheme_id')
        service_date = claim_data.get('service_date')
        if scheme_id and service_date:
            result = self.scheme_validator.validate_scheme_termination(scheme_id, service_date)
            results.append(result)
        
        # 2. Check for duplicate claim
        claim_number = claim_data.get('claimform_number')
        if claim_number:
            result = self.duplicate_checker.check_duplicate_claim(claim_number)
            results.append(result)
        
        # 3. Check for duplicate invoice
        invoice_number = claim_data.get('invoice_number')
        hospital_id = claim_data.get('hospital_id')
        if invoice_number and hospital_id:
            result = self.duplicate_checker.check_duplicate_invoice(invoice_number, hospital_id)
            results.append(result)
        
        # 4. Validate hospital pricing
        service_code = claim_data.get('service_code')
        amount = claim_data.get('amount')
        if hospital_id and service_code and amount:
            result = self.price_validator.validate_hospital_price_agreement(
                hospital_id, service_code, amount
            )
            results.append(result)
        
        return results
    
    def calculate_claim_financials(self, claim_data: Dict[str, Any]) -> Dict[str, Decimal]:
        """Calculate claim financial details"""
        claim_amount = Decimal(str(claim_data.get('amount', 0)))
        member_scheme = claim_data.get('scheme_id')
        benefit_code = claim_data.get('benefit_code')
        
        co_payment = self.benefit_calculator.calculate_co_payment(
            claim_amount, member_scheme, benefit_code
        )
        
        benefit_amount = claim_amount - co_payment
        
        return {
            'total_amount': claim_amount,
            'co_payment': co_payment,
            'benefit_amount': benefit_amount
        }


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class BusinessRulesFactory:
    """Factory for creating business rule instances"""
    
    @staticmethod
    def create_claim_business_rules() -> ClaimBusinessRules:
        """Create configured claim business rules"""
        return ClaimBusinessRules(
            scheme_validator=SchemeTerminationValidator(),
            duplicate_checker=DuplicateClaimChecker(),
            price_validator=HospitalPriceValidator(),
            benefit_calculator=BenefitCalculator()
        )


# =============================================================================
# BUSINESS RULE SERVICE (SOLID: Single Responsibility Principle)
# =============================================================================

class ClaimBusinessRuleService:
    """
    Service for applying business rules to claims
    Single responsibility: Orchestrate business rule validation
    """
    
    def __init__(self, business_rules: ClaimBusinessRules):
        self.business_rules = business_rules
    
    @transaction.atomic
    def validate_and_process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process claim with business rules"""
        # Validate claim
        validation_results = self.business_rules.validate_claim_submission(claim_data)
        
        # Check if any validation failed
        failed_validations = [r for r in validation_results if not r.is_valid]
        if failed_validations:
            return {
                'success': False,
                'errors': [{'code': r.error_code, 'message': r.message} for r in failed_validations]
            }
        
        # Calculate financials
        financials = self.business_rules.calculate_claim_financials(claim_data)
        
        return {
            'success': True,
            'financials': financials,
            'validation_results': validation_results
        }
