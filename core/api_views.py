"""
REST API Views for HMS Ultra Core Modules
Implements comprehensive API endpoints for all core functionality
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .claim_workflow import ClaimWorkflowFactory
from .audit_trail import AuditTrailFactory
from .notification_system import NotificationServiceFactory
from .provider_management import ProviderManagementFactory
from .reporting_engine import ReportingEngineFactory
from .permissions import (
    CanApproveClaims, CanProcessPayments, CanViewAuditTrail, 
    CanManageProviders, CanGenerateReports, CanSendNotifications
)

logger = logging.getLogger(__name__)


# =============================================================================
# CLAIM WORKFLOW API ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def submit_claim(request):
    """Submit a new claim for processing"""
    try:
        workflow_service = ClaimWorkflowFactory.create_claim_workflow_service()
        result = workflow_service.submit_claim(request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error submitting claim: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanApproveClaims])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def approve_claim(request, claim_id):
    """Approve a submitted claim"""
    try:
        workflow_service = ClaimWorkflowFactory.create_claim_workflow_service()
        approver_id = request.user.id
        result = workflow_service.approve_claim(claim_id, approver_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error approving claim {claim_id}: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def reject_claim(request, claim_id):
    """Reject a submitted claim"""
    try:
        workflow_service = ClaimWorkflowFactory.create_claim_workflow_service()
        rejector_id = request.user.id
        reason = request.data.get('reason', 'No reason provided')
        result = workflow_service.reject_claim(claim_id, reason, rejector_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error rejecting claim {claim_id}: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanProcessPayments])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def process_payment(request, claim_id):
    """Process payment for an approved claim"""
    try:
        workflow_service = ClaimWorkflowFactory.create_claim_workflow_service()
        payment_data = request.data
        result = workflow_service.process_claim_payment(claim_id, payment_data)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error processing payment for claim {claim_id}: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_claim_status(request, claim_id):
    """Get current status of a claim"""
    try:
        workflow_service = ClaimWorkflowFactory.create_claim_workflow_service()
        result = workflow_service.get_claim_workflow_status(claim_id)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(result, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error getting claim status for {claim_id}: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# AUDIT TRAIL API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewAuditTrail])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_audit_trail(request):
    """Get audit trail for specified date range"""
    try:
        audit_service = AuditTrailFactory.create_audit_trail_service()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        user_id = request.GET.get('user_id')
        
        if start_date and end_date:
            result = audit_service.get_audit_trail(start_date, end_date)
        elif user_id:
            result = audit_service.get_user_audit_trail(user_id, start_date, end_date)
        else:
            return Response({
                'error': 'start_date and end_date or user_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def export_audit_trail(request):
    """Export audit trail to specified format"""
    try:
        audit_service = AuditTrailFactory.create_audit_trail_service()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        format_type = request.GET.get('format', 'CSV')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = audit_service.export_audit_trail(start_date, end_date, format_type)
        return Response({'export_path': result}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error exporting audit trail: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# NOTIFICATION API ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanSendNotifications])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def send_notification(request):
    """Send notification to specified recipient"""
    try:
        notification_service = NotificationServiceFactory.create_notification_service()
        result = notification_service.send_notification(
            recipient=request.data.get('recipient'),
            message=request.data.get('message'),
            notification_type=request.data.get('type', 'EMAIL'),
            priority=request.data.get('priority', 'NORMAL')
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PROVIDER MANAGEMENT API ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageProviders])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def register_provider(request):
    """Register a new healthcare provider"""
    try:
        provider_service = ProviderManagementFactory.create_provider_management_service()
        result = provider_service.register_provider(request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error registering provider: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def activate_provider(request, provider_id):
    """Activate a healthcare provider"""
    try:
        provider_service = ProviderManagementFactory.create_provider_management_service()
        result = provider_service.activate_provider(provider_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error activating provider {provider_id}: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def deactivate_provider(request, provider_id):
    """Deactivate a healthcare provider"""
    try:
        provider_service = ProviderManagementFactory.create_provider_management_service()
        reason = request.data.get('reason', 'No reason provided')
        result = provider_service.deactivate_provider(provider_id, reason)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error deactivating provider {provider_id}: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_provider_services(request, provider_id):
    """Get all services for a provider"""
    try:
        provider_service = ProviderManagementFactory.create_provider_management_service()
        result = provider_service.get_provider_services(provider_id)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting provider services for {provider_id}: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# REPORTING API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_dashboard_metrics(request):
    """Get dashboard metrics and KPIs"""
    try:
        reporting_service = ReportingEngineFactory.create_reporting_engine()
        result = reporting_service.get_dashboard_metrics()
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanGenerateReports])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def generate_report(request):
    """Generate a custom report"""
    try:
        reporting_service = ReportingEngineFactory.create_reporting_engine()
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        format_type = request.data.get('format', 'CSV')
        
        result = reporting_service.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            format_type=format_type
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return Response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    return Response({
        'status': 'healthy',
        'service': 'HMS Ultra API',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
