"""
Billing Session Management
Implements SOLID principles for period-based financial control
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from django.db import transaction, models
from django.utils import timezone

from .models import BillingSession, FinancialPeriod, Claim, ClaimPayment


class BillingSessionStatus(Enum):
    """Billing session status enumeration"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LOCKED = "LOCKED"


class PeriodType(Enum):
    """Financial period type enumeration"""
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


# =============================================================================
# INTERFACES (SOLID: Interface Segregation Principle)
# =============================================================================

class IBillingSessionValidator(ABC):
    """Interface for billing session validation"""
    
    @abstractmethod
    def validate_session_dates(self, start_date: date, end_date: date) -> bool:
        pass
    
    @abstractmethod
    def validate_session_overlap(self, start_date: date, end_date: date) -> bool:
        pass


class IBillingSessionCalculator(ABC):
    """Interface for billing session calculations"""
    
    @abstractmethod
    def calculate_session_totals(self, session_id: str) -> Dict[str, Decimal]:
        pass
    
    @abstractmethod
    def calculate_claim_totals(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Decimal]:
        pass


class IBillingSessionManager(ABC):
    """Interface for billing session management"""
    
    @abstractmethod
    def create_billing_session(
        self, 
        start_date: date, 
        end_date: date, 
        created_by: str
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def close_billing_session(self, session_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_current_session(self, service_date: date) -> Optional[BillingSession]:
        pass


# =============================================================================
# CONCRETE IMPLEMENTATIONS (SOLID: Single Responsibility Principle)
# =============================================================================

class BillingSessionValidator(IBillingSessionValidator):
    """Validates billing session data and rules"""
    
    def validate_session_dates(self, start_date: date, end_date: date) -> bool:
        """Validate billing session dates"""
        # Check if start date is before end date
        if start_date >= end_date:
            return False
        
        # Check if dates are not in the future
        today = timezone.now().date()
        if start_date > today or end_date > today:
            return False
        
        return True
    
    def validate_session_overlap(self, start_date: date, end_date: date) -> bool:
        """Validate no overlapping sessions"""
        # Check for overlapping sessions
        overlapping_sessions = BillingSession.objects.filter(
            models.Q(from_date__lte=end_date, to_date__gte=start_date)
        ).exclude(status='CLOSED')
        
        return not overlapping_sessions.exists()


class BillingSessionCalculator(IBillingSessionCalculator):
    """Calculates billing session totals and statistics"""
    
    def calculate_session_totals(self, session_id: str) -> Dict[str, Decimal]:
        """Calculate totals for a billing session"""
        try:
            session = BillingSession.objects.get(id=session_id)
            
            # Calculate claim totals for the session period
            claim_totals = self.calculate_claim_totals(
                session.from_date, session.to_date
            )
            
            return {
                'total_claims': claim_totals['total_claims'],
                'total_amount': claim_totals['total_amount'],
                'approved_claims': claim_totals['approved_claims'],
                'approved_amount': claim_totals['approved_amount'],
                'paid_claims': claim_totals['paid_claims'],
                'paid_amount': claim_totals['paid_amount']
            }
            
        except BillingSession.DoesNotExist:
            return {
                'total_claims': Decimal('0'),
                'total_amount': Decimal('0'),
                'approved_claims': Decimal('0'),
                'approved_amount': Decimal('0'),
                'paid_claims': Decimal('0'),
                'paid_amount': Decimal('0')
            }
    
    def calculate_claim_totals(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Decimal]:
        """Calculate claim totals for a date range"""
        # Get claims in the date range
        claims = Claim.objects.filter(
            service_date__gte=start_date,
            service_date__lte=end_date
        )
        
        # Calculate totals
        total_claims = claims.count()
        total_amount = claims.aggregate(
            total=models.Sum('hospital_claimamount')
        )['total'] or Decimal('0')
        
        # Approved claims
        approved_claims = claims.filter(transaction_status='APPROVED')
        approved_count = approved_claims.count()
        approved_amount = approved_claims.aggregate(
            total=models.Sum('hospital_claimamount')
        )['total'] or Decimal('0')
        
        # Paid claims
        paid_claims = claims.filter(transaction_status='PAID')
        paid_count = paid_claims.count()
        paid_amount = paid_claims.aggregate(
            total=models.Sum('hospital_claimamount')
        )['total'] or Decimal('0')
        
        return {
            'total_claims': total_claims,
            'total_amount': total_amount,
            'approved_claims': approved_count,
            'approved_amount': approved_amount,
            'paid_claims': paid_count,
            'paid_amount': paid_amount
        }


class BillingSessionManager(IBillingSessionManager):
    """Manages billing sessions"""
    
    def __init__(
        self, 
        validator: IBillingSessionValidator, 
        calculator: IBillingSessionCalculator
    ):
        self.validator = validator
        self.calculator = calculator
    
    @transaction.atomic
    def create_billing_session(
        self, 
        start_date: date, 
        end_date: date, 
        created_by: str
    ) -> Dict[str, Any]:
        """Create a new billing session"""
        # Validate dates
        if not self.validator.validate_session_dates(start_date, end_date):
            return {
                'success': False,
                'message': 'Invalid session dates'
            }
        
        # Check for overlapping sessions
        if not self.validator.validate_session_overlap(start_date, end_date):
            return {
                'success': False,
                'message': 'Session dates overlap with existing session'
            }
        
        # Create billing session
        session = BillingSession.objects.create(
            from_date=start_date,
            to_date=end_date,
            session_status='OPEN',
            created_by=created_by
        )
        
        # Calculate initial totals
        totals = self.calculator.calculate_session_totals(session.id)
        session.total_claims = totals['total_claims']
        session.total_amount = totals['total_amount']
        session.save()
        
        return {
            'success': True,
            'message': 'Billing session created successfully',
            'session_id': session.id,
            'totals': totals
        }
    
    @transaction.atomic
    def close_billing_session(self, session_id: str) -> Dict[str, Any]:
        """Close a billing session"""
        try:
            session = BillingSession.objects.get(id=session_id)
            
            # Check if session is already closed
            if session.session_status == 'CLOSED':
                return {
                    'success': False,
                    'message': 'Session is already closed'
                }
            
            # Calculate final totals
            totals = self.calculator.calculate_session_totals(session_id)
            
            # Update session with final totals
            session.total_claims = totals['total_claims']
            session.total_amount = totals['total_amount']
            session.session_status = 'CLOSED'
            session.save()
            
            return {
                'success': True,
                'message': 'Billing session closed successfully',
                'final_totals': totals
            }
            
        except BillingSession.DoesNotExist:
            return {
                'success': False,
                'message': 'Billing session not found'
            }
    
    def get_current_session(self, service_date: date) -> Optional[BillingSession]:
        """Get current billing session for a service date"""
        try:
            session = BillingSession.objects.filter(
                from_date__lte=service_date,
                to_date__gte=service_date,
                session_status='OPEN'
            ).first()
            
            return session
            
        except Exception:
            return None


# =============================================================================
# BUSINESS RULE COMPOSER (SOLID: Open/Closed Principle)
# =============================================================================

class BillingSessionService:
    """
    Composes billing session management
    Follows Open/Closed Principle - open for extension, closed for modification
    """
    
    def __init__(
        self,
        validator: IBillingSessionValidator,
        calculator: IBillingSessionCalculator,
        manager: IBillingSessionManager
    ):
        self.validator = validator
        self.calculator = calculator
        self.manager = manager
    
    def create_monthly_session(
        self, 
        year: int, 
        month: int, 
        created_by: str
    ) -> Dict[str, Any]:
        """Create monthly billing session"""
        # Calculate month start and end dates
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return self.manager.create_billing_session(
            start_date, end_date, created_by
        )
    
    def create_quarterly_session(
        self, 
        year: int, 
        quarter: int, 
        created_by: str
    ) -> Dict[str, Any]:
        """Create quarterly billing session"""
        # Calculate quarter start and end dates
        quarter_start_month = (quarter - 1) * 3 + 1
        start_date = date(year, quarter_start_month, 1)
        
        quarter_end_month = quarter * 3
        if quarter_end_month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, quarter_end_month + 1, 1) - timedelta(days=1)
        
        return self.manager.create_billing_session(
            start_date, end_date, created_by
        )
    
    def validate_service_date(self, service_date: date) -> Dict[str, Any]:
        """Validate if service date is within an open billing session"""
        session = self.manager.get_current_session(service_date)
        
        if not session:
            return {
                'valid': False,
                'message': 'No open billing session for this date',
                'session_id': None
            }
        
        return {
            'valid': True,
            'message': 'Service date is within open billing session',
            'session_id': session.id,
            'session_period': f"{session.from_date} to {session.to_date}"
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        try:
            session = BillingSession.objects.get(id=session_id)
            totals = self.calculator.calculate_session_totals(session_id)
            
            return {
                'session_id': session.id,
                'period': f"{session.from_date} to {session.to_date}",
                'status': session.session_status,
                'totals': totals,
                'created_by': session.created_by,
                'created_date': session.created_date
            }
            
        except BillingSession.DoesNotExist:
            return {
                'error': 'Billing session not found'
            }


# =============================================================================
# FACTORY PATTERN (SOLID: Dependency Inversion Principle)
# =============================================================================

class BillingSessionFactory:
    """Factory for creating billing session instances"""
    
    @staticmethod
    def create_billing_session_service() -> BillingSessionService:
        """Create configured billing session service"""
        validator = BillingSessionValidator()
        calculator = BillingSessionCalculator()
        manager = BillingSessionManager(validator, calculator)
        
        return BillingSessionService(validator, calculator, manager)
