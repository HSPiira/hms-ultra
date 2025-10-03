"""
API Integration Service
Integrates business logic with existing APIs
"""

from typing import Dict, Any, List
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from .business_logic_service import get_business_logic_service
from .claim_workflow import ClaimWorkflowFactory
from .provider_management import ProviderManagementFactory
from .notification_system import NotificationServiceFactory
from .audit_trail import AuditTrailFactory


class APIBusinessLogicIntegration:
    """Integrates business logic with API endpoints"""
    
    def __init__(self):
        self.business_service = get_business_logic_service()
        self.claim_workflow = ClaimWorkflowFactory.create_claim_workflow_service()
        self.provider_management = ProviderManagementFactory.create_provider_management_service()
        self.notification_service = NotificationServiceFactory.create_notification_service()
        self.audit_service = AuditTrailFactory.create_audit_trail_service()
    
    def process_claim_with_business_logic(self, claim_data: Dict[str, Any], user_id: str) -> Response:
        """Process claim with complete business logic integration"""
        try:
            # 1. Submit claim through workflow
            workflow_result = self.claim_workflow.submit_claim(claim_data)
            
            if not workflow_result['success']:
                return Response(
                    {'error': workflow_result.get('errors', ['Unknown error'])},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            claim_id = workflow_result['claim_id']
            
            # 2. Log audit trail
            self.audit_service.log_claim_creation(
                claim_id, user_id, claim_data
            )
            
            # 3. Send notifications
            self.notification_service.notify_claim_submitted(claim_id)
            
            # 4. Apply business rules validation
            business_result = self.business_service.validate_claim_eligibility({
                'member_id': claim_data.get('member_id'),
                'scheme_id': claim_data.get('scheme_id'),
                'hospital_id': claim_data.get('hospital_id'),
                'service_date': claim_data.get('service_date'),
                'claimform_number': claim_data.get('claimform_number'),
                'invoice_number': claim_data.get('invoice_number'),
                'amount': claim_data.get('hospital_claimamount'),
                'benefit_code': 'GENERAL'
            })
            
            if business_result['success']:
                # Auto-approve if business rules pass
                approval_result = self.claim_workflow.approve_claim(claim_id, user_id)
                if approval_result['success']:
                    self.audit_service.log_claim_approval(claim_id, user_id, user_id)
                    self.notification_service.notify_claim_approved(claim_id)
            
            return Response({
                'success': True,
                'claim_id': claim_id,
                'workflow_result': workflow_result,
                'business_validation': business_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def process_member_with_business_logic(self, member_data: Dict[str, Any], user_id: str) -> Response:
        """Process member with complete business logic integration"""
        try:
            # 1. Create member through business logic
            member_result = self.business_service.process_member_enrollment_workflow(
                member_data, member_data.get('scheme_id')
            )
            
            if not member_result['success']:
                return Response(
                    {'error': member_result.get('message', 'Member creation failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            member_id = member_data.get('id')
            
            # 2. Log audit trail
            self.audit_service.log_member_creation(member_id, user_id, member_data)
            
            # 3. Send notifications
            self.notification_service.notify_member_enrolled(member_id)
            
            return Response({
                'success': True,
                'member_id': member_id,
                'result': member_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def process_provider_with_business_logic(self, provider_data: Dict[str, Any], user_id: str) -> Response:
        """Process provider with complete business logic integration"""
        try:
            # 1. Register provider through business logic
            provider_result = self.provider_management.register_new_provider(provider_data)
            
            if not provider_result['success']:
                return Response(
                    {'error': provider_result.get('error', 'Provider registration failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            provider_id = provider_result['provider_id']
            
            # 2. Log audit trail
            self.audit_service.log_provider_registration(provider_id, user_id, provider_data)
            
            # 3. Send notifications
            self.notification_service.notify_provider_registered(provider_id)
            
            return Response({
                'success': True,
                'provider_id': provider_id,
                'result': provider_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_dashboard_metrics(self) -> Response:
        """Get dashboard metrics with business logic"""
        try:
            from datetime import date, timedelta
            
            # Get metrics for last 30 days
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            # Get business metrics
            metrics = self.business_service.get_session_summary('current')
            
            return Response({
                'success': True,
                'metrics': metrics,
                'period': f"{start_date} to {end_date}"
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
