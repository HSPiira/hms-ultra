"""
Tests for Business Logic Components
Tests SOLID principles implementation
"""

from datetime import date, datetime
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from .business_logic_service import get_business_logic_service
from .models import (
    Company, CompanyType, Scheme, Member, Hospital, Benefit, 
    SchemeBenefit, BillingSession, Claim
)


class BusinessLogicTestCase(TestCase):
    """Test case for business logic components"""
    
    def setUp(self):
        """Set up test data"""
        # Create company type
        self.company_type = CompanyType.objects.create(
            type_name='Test Company Type',
            description='Test description'
        )
        
        # Create company
        self.company = Company.objects.create(
            company_name='Test Company',
            company_type=self.company_type,
            currentupdate='ACTIVE'
        )
        
        # Create scheme
        self.scheme = Scheme.objects.create(
            scheme_name='Test Scheme',
            company=self.company,
            limit_value=Decimal('10000.00'),
            beginningdate=date(2024, 1, 1),
            endingdate=date(2024, 12, 31)
        )
        
        # Create member
        self.member = Member.objects.create(
            member_name='Test Member',
            card_number='CARD001',
            company=self.company,
            scheme=self.scheme,
            member_status='ACTIVE'
        )
        
        # Create hospital
        self.hospital = Hospital.objects.create(
            hospital_name='Test Hospital',
            hospital_reference='HOSP001',
            status='ACTIVE'
        )
        
        # Create benefit
        self.benefit = Benefit.objects.create(
            service_name='Test Service',
            status='ACTIVE'
        )
        
        # Create scheme benefit
        self.scheme_benefit = SchemeBenefit.objects.create(
            scheme=self.scheme,
            scheme_benefit=self.benefit,
            limit_amount=Decimal('5000.00'),
            copayment_percent=Decimal('20.00')
        )
        
        # Create billing session
        self.billing_session = BillingSession.objects.create(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            session_status='OPEN',
            created_by='test_user'
        )
    
    def test_claim_business_rules_validation(self):
        """Test claim business rules validation"""
        business_service = get_business_logic_service()
        
        # Test valid claim data
        claim_data = {
            'member_id': str(self.member.id),
            'scheme_id': str(self.scheme.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date(2024, 1, 15),
            'claimform_number': 'CLM001',
            'invoice_number': 'INV001',
            'amount': Decimal('1000.00'),
            'benefit_code': 'Test Service'
        }
        
        result = business_service.validate_claim_eligibility(claim_data)
        self.assertTrue(result['success'])
    
    def test_member_lifecycle_activation(self):
        """Test member activation workflow"""
        business_service = get_business_logic_service()
        
        # Deactivate member first
        self.member.member_status = 'INACTIVE'
        self.member.save()
        
        # Activate member
        result = business_service.activate_member(
            str(self.member.id),
            date(2024, 1, 1),
            'Test activation'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['member_status'], 'ACTIVE')
    
    def test_financial_processing_calculation(self):
        """Test financial processing calculations"""
        business_service = get_business_logic_service()
        
        claim_data = {
            'amount': Decimal('1000.00'),
            'scheme_id': str(self.scheme.id),
            'benefit_code': 'Test Service',
            'member_id': str(self.member.id),
            'service_date': date(2024, 1, 15)
        }
        
        financials = business_service.calculate_claim_financials(claim_data)
        
        # Check co-payment calculation (20% of 1000 = 200)
        expected_co_payment = Decimal('200.00')
        self.assertEqual(financials['co_payment'], expected_co_payment)
        
        # Check benefit amount (1000 - 200 = 800)
        expected_benefit_amount = Decimal('800.00')
        self.assertEqual(financials['benefit_amount'], expected_benefit_amount)
    
    def test_billing_session_validation(self):
        """Test billing session validation"""
        business_service = get_business_logic_service()
        
        # Test valid service date
        result = business_service.validate_service_date(date(2024, 1, 15))
        self.assertTrue(result['valid'])
        
        # Test invalid service date (outside session)
        result = business_service.validate_service_date(date(2024, 2, 15))
        self.assertFalse(result['valid'])
    
    def test_complete_claim_workflow(self):
        """Test complete claim processing workflow"""
        business_service = get_business_logic_service()
        
        claim_data = {
            'member_id': str(self.member.id),
            'scheme_id': str(self.scheme.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date(2024, 1, 15),
            'claimform_number': 'CLM002',
            'invoice_number': 'INV002',
            'amount': Decimal('1500.00'),
            'benefit_code': 'Test Service'
        }
        
        result = business_service.process_complete_claim_workflow(claim_data)
        self.assertTrue(result['success'])
    
    def test_member_enrollment_workflow(self):
        """Test member enrollment workflow"""
        business_service = get_business_logic_service()
        
        member_data = {
            'id': str(self.member.id),
            'member_name': 'New Member',
            'company_id': str(self.company.id),
            'scheme_id': str(self.scheme.id)
        }
        
        result = business_service.process_member_enrollment_workflow(
            member_data, str(self.scheme.id)
        )
        self.assertTrue(result['success'])
    
    def test_scheme_termination_validation(self):
        """Test scheme termination validation"""
        business_service = get_business_logic_service()
        
        # Test with active scheme
        claim_data = {
            'scheme_id': str(self.scheme.id),
            'service_date': date(2024, 1, 15)
        }
        
        result = business_service.validate_claim_eligibility(claim_data)
        self.assertTrue(result['success'])
        
        # Test with terminated scheme
        self.scheme.terminationdate = date(2024, 1, 10)
        self.scheme.save()
        
        result = business_service.validate_claim_eligibility(claim_data)
        self.assertFalse(result['success'])
    
    def test_duplicate_claim_validation(self):
        """Test duplicate claim validation"""
        business_service = get_business_logic_service()
        
        # Create existing claim
        Claim.objects.create(
            member=self.member,
            hospital=self.hospital,
            claimform_number='CLM003',
            invoice_number='INV003',
            service_date=date(2024, 1, 15),
            hospital_claimamount=Decimal('1000.00'),
            transaction_status='PENDING'
        )
        
        # Test duplicate claim
        claim_data = {
            'member_id': str(self.member.id),
            'scheme_id': str(self.scheme.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date(2024, 1, 15),
            'claimform_number': 'CLM003',  # Duplicate
            'invoice_number': 'INV004',
            'amount': Decimal('1000.00'),
            'benefit_code': 'Test Service'
        }
        
        result = business_service.validate_claim_eligibility(claim_data)
        self.assertFalse(result['success'])
        self.assertIn('DUPLICATE_CLAIM', [error['code'] for error in result['errors']])
    
    def test_payment_eligibility_validation(self):
        """Test payment eligibility validation"""
        business_service = get_business_logic_service()
        
        # Create approved claim
        claim = Claim.objects.create(
            member=self.member,
            hospital=self.hospital,
            claimform_number='CLM004',
            invoice_number='INV004',
            service_date=date(2024, 1, 15),
            hospital_claimamount=Decimal('1000.00'),
            member_claimamount=Decimal('800.00'),
            transaction_status='APPROVED'
        )
        
        # Test valid payment
        result = business_service.validate_payment_eligibility(
            str(claim.id), Decimal('800.00')
        )
        self.assertTrue(result['eligible'])
        
        # Test invalid payment (exceeds benefit amount)
        result = business_service.validate_payment_eligibility(
            str(claim.id), Decimal('1000.00')
        )
        self.assertFalse(result['eligible'])
    
    def test_billing_session_creation(self):
        """Test billing session creation"""
        business_service = get_business_logic_service()
        
        result = business_service.create_monthly_billing_session(
            2024, 2, 'test_user'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('session_id', result)
    
    def test_member_category_change(self):
        """Test member category change"""
        business_service = get_business_logic_service()
        
        result = business_service.change_member_category(
            str(self.member.id),
            'Premium',
            date(2024, 1, 1)
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_category'], 'Premium')
