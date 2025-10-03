"""
Test cases for claim workflow functionality
"""

from decimal import Decimal
from datetime import date
from django.test import TestCase
from .tests import CoreModuleTestCase
from .claim_workflow import ClaimWorkflowServiceFactory


class ClaimWorkflowTestCase(CoreModuleTestCase):
    """Test cases for claim workflow functionality"""
    
    def test_claim_submission(self):
        """Test claim submission workflow"""
        workflow_service = ClaimWorkflowServiceFactory.create_service()
        
        claim_data = {
            'member_id': str(self.member.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date.today(),
            'claimform_number': 'CF-001',
            'invoice_number': 'INV-001',
            'hospital_claimamount': Decimal('150.00'),
            'created_by': 'testuser'
        }
        
        result = workflow_service.submit_claim(claim_data)
        
        self.assertTrue(result['success'])
        self.assertIn('claim_id', result)
        self.assertEqual(result['stage'], 'DATA_VALIDATION')
    
    def test_claim_approval(self):
        """Test claim approval workflow"""
        workflow_service = ClaimWorkflowServiceFactory.create_service()
        
        # First submit a claim
        claim_data = {
            'member_id': str(self.member.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date.today(),
            'claimform_number': 'CF-002',
            'invoice_number': 'INV-002',
            'hospital_claimamount': Decimal('200.00'),
            'created_by': 'testuser'
        }
        
        submit_result = workflow_service.submit_claim(claim_data)
        claim_id = submit_result['claim_id']
        
        # Then approve the claim
        result = workflow_service.approve_claim(claim_id, str(self.user.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['stage'], 'APPROVAL')
    
    def test_claim_rejection(self):
        """Test claim rejection workflow"""
        workflow_service = ClaimWorkflowServiceFactory.create_service()
        
        # First submit a claim
        claim_data = {
            'member_id': str(self.member.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date.today(),
            'claimform_number': 'CF-003',
            'invoice_number': 'INV-003',
            'hospital_claimamount': Decimal('300.00'),
            'created_by': 'testuser'
        }
        
        submit_result = workflow_service.submit_claim(claim_data)
        claim_id = submit_result['claim_id']
        
        # Then reject the claim
        result = workflow_service.reject_claim(
            claim_id, 
            'Insufficient documentation', 
            str(self.user.id)
        )
        
        self.assertTrue(result['success'])
    
    def test_claim_payment_processing(self):
        """Test claim payment processing"""
        workflow_service = ClaimWorkflowServiceFactory.create_service()
        
        # First submit and approve a claim
        claim_data = {
            'member_id': str(self.member.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date.today(),
            'claimform_number': 'CF-004',
            'invoice_number': 'INV-004',
            'hospital_claimamount': Decimal('400.00'),
            'created_by': 'testuser'
        }
        
        submit_result = workflow_service.submit_claim(claim_data)
        claim_id = submit_result['claim_id']
        
        approve_result = workflow_service.approve_claim(claim_id, str(self.user.id))
        self.assertTrue(approve_result['success'])
        
        # Then process payment
        payment_data = {
            'amount': Decimal('400.00'),
            'payment_method': 'BANK_TRANSFER',
            'payment_reference': 'PAY-001'
        }
        
        result = workflow_service.process_claim_payment(claim_id, payment_data)
        self.assertTrue(result['success'])
