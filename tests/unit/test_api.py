"""
Test cases for API endpoints
"""

from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Claim, Hospital, Member, Company, Service, Scheme
from .tests import CoreModuleTestCase


class CoreAPITestCase(APITestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up API test data"""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test data
        self.company = Company.objects.create(
            company_name='API Test Company',
            contact_person='API Test',
            company_address='123 API Street',
            phone_number='+1-555-API01',
            email='api@testcompany.com'
        )
        
        self.scheme = Scheme.objects.create(
            scheme_name='API Test Scheme',
            company=self.company,
            beginningdate=date.today(),
            endingdate=date.today() + timedelta(days=365)
        )
        
        self.member = Member.objects.create(
            card_number='API001',
            member_name='API User',
            email='api.user@example.com',
            phone_mobile='+1-555-API01',
            company=self.company,
            scheme=self.scheme
        )
        
        self.hospital = Hospital.objects.create(
            hospital_reference='API001',
            hospital_name='API Test Hospital',
            hospital_address='456 API Hospital Street',
            contact_person='Dr. API',
            hospital_email='api@testhospital.com',
            hospital_phone_number='+1-555-API02'
        )
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_claim_submission_api(self):
        """Test claim submission API endpoint"""
        claim_data = {
            'member_id': str(self.member.id),
            'hospital_id': str(self.hospital.id),
            'service_date': date.today().isoformat(),
            'claimform_number': 'API-CF-001',
            'invoice_number': 'API-INV-001',
            'hospital_claimamount': 150.00,
            'created_by': 'apiuser'
        }
        
        response = self.client.post('/api/claims/submit/', claim_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_provider_registration_api(self):
        """Test provider registration API endpoint"""
        provider_data = {
            'hospital_reference': 'API-H002',
            'hospital_name': 'API Medical Center',
            'hospital_address': '789 API Medical Street',
            'contact_person': 'Dr. API Medical',
            'hospital_email': 'api@medicalcenter.com',
            'hospital_phone_number': '+1-555-API03'
        }
        
        response = self.client.post('/api/providers/register/', provider_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_notification_sending_api(self):
        """Test notification sending API endpoint"""
        notification_data = {
            'recipient': 'test@example.com',
            'message': 'API test notification',
            'notification_type': 'EMAIL',
            'priority': 'NORMAL'
        }
        
        response = self.client.post('/api/notifications/send/', notification_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_dashboard_metrics_api(self):
        """Test dashboard metrics API endpoint"""
        response = self.client.get('/api/reports/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_claims', response.data)
    
    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints"""
        # Create client without authentication
        unauthenticated_client = APIClient()
        
        response = unauthenticated_client.get('/api/reports/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
