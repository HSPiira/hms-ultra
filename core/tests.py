"""
Comprehensive Test Suite for HMS Ultra Core Modules
Implements unit tests, integration tests, and end-to-end testing scenarios
"""

import json
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Claim, Hospital, Member, Company, Service, Medicine, LabTest
from .claim_workflow import ClaimWorkflowServiceFactory
from .audit_trail import AuditTrailServiceFactory
from .notification_system import NotificationServiceFactory
from .provider_management import ProviderManagementServiceFactory
from .reporting_engine import ReportingEngineFactory


class CoreModuleTestCase(TestCase):
    """Base test case for core modules"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create test company
        self.company = Company.objects.create(
            company_name='Test Insurance Company',
            contact_person='John Doe',
            company_address='123 Test Street',
            phone_number='+1-555-0123',
            email='contact@testinsurance.com'
        )
        
        # Create test member
        self.member = Member.objects.create(
            member_number='M001',
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='+1-555-0124',
            company=self.company
        )
        
        # Create test hospital
        self.hospital = Hospital.objects.create(
            hospital_reference='H001',
            hospital_name='Test General Hospital',
            hospital_address='456 Hospital Street',
            contact_person='Dr. Test',
            hospital_email='contact@testhospital.com',
            hospital_phone_number='+1-555-0125'
        )
        
        # Create test service
        self.service = Service.objects.create(
            service_code='S001',
            service_name='General Consultation',
            service_category='Consultation',
            description='General medical consultation',
            base_amount=Decimal('100.00')
        )