"""
REST API Views for HMS Ultra Core Modules
Implements comprehensive API endpoints for all core functionality
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from core.permissions.permissions import CanViewAuditTrail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

# Import schema decorators
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    ClaimSubmissionSerializer, ClaimApprovalSerializer, ClaimRejectionSerializer,
    PaymentProcessingSerializer, ProviderRegistrationSerializer, 
    ProviderDeactivationSerializer, NotificationSerializer, ReportGenerationSerializer,
    AuditTrailQuerySerializer, ClaimStatusSerializer, DashboardMetricsSerializer,
    ErrorResponseSerializer, SuccessResponseSerializer
)

from core.services.claim_workflow import ClaimWorkflowFactory
from core.services.business_logic_service import get_business_logic_service
from core.utils.result import OperationResult
from core.services.audit_trail import AuditTrailFactory
from core.services.notification_system import NotificationServiceFactory
from core.services.provider_management import ProviderManagementFactory
from core.services.reporting_engine import ReportingEngineFactory
from core.services.reporting_engine import ReportType, ReportFormat
from core.permissions.permissions import (
    CanApproveClaims, CanProcessPayments, CanViewAuditTrail, 
    CanManageProviders, CanGenerateReports, CanSendNotifications
)

logger = logging.getLogger(__name__)


# =============================================================================
# CLAIM WORKFLOW API ENDPOINTS
# =============================================================================

@extend_schema(
    summary="Submit a new claim",
    description="Submit a new healthcare claim for processing",
    request=ClaimSubmissionSerializer,
    responses={
        201: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    examples=[
        OpenApiExample(
            'Valid Claim Submission',
            summary='Example claim submission',
            description='Example of a valid claim submission',
            value={
                'member_id': 'cm1234567890123456789012345',
                'hospital_id': 'cm1234567890123456789012346',
                'service_date': '2024-01-15',
                'claimform_number': 'CF-2024-001',
                'invoice_number': 'INV-2024-001',
                'hospital_claimamount': 1500.00,
                'created_by': 'system'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def submit_claim(request):
    """Submit a new claim for processing"""
    try:
        # For end-to-end workflow, use business logic service boundary
        bl = get_business_logic_service()
        op: OperationResult = bl.process_claim_submission(request.data)
        if op.success:
            return Response(op.data or { 'success': True }, status=status.HTTP_201_CREATED)
        return Response({ 'success': False, 'error': op.error, 'error_code': op.error_code, **(op.data or {}) }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception:
        logger.exception("Error submitting claim")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Approve a claim",
    description="Approve a submitted claim for payment processing",
    request=ClaimApprovalSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='claim_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the claim'
        )
    ],
    examples=[
        OpenApiExample(
            'Claim Approval',
            summary='Example claim approval',
            description='Example of approving a claim',
            value={
                'approver_id': 'cm1234567890123456789012347',
                'approval_notes': 'Claim approved after review'
            }
        )
    ]
)
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
            
    except Exception:
        logger.exception(f"Error approving claim {claim_id}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Reject a claim",
    description="Reject a submitted claim with reason",
    request=ClaimRejectionSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='claim_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the claim'
        )
    ],
    examples=[
        OpenApiExample(
            'Claim Rejection',
            summary='Example claim rejection',
            description='Example of rejecting a claim',
            value={
                'reason': 'Insufficient documentation provided',
                'rejector_id': 'cm1234567890123456789012347'
            }
        )
    ]
)
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
            
    except Exception:
        logger.exception(f"Error rejecting claim {claim_id}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Process claim payment",
    description="Process payment for an approved claim",
    request=PaymentProcessingSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='claim_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the claim'
        )
    ],
    examples=[
        OpenApiExample(
            'Payment Processing',
            summary='Example payment processing',
            description='Example of processing a claim payment',
            value={
                'amount': 1200.00,
                'payment_method': 'BANK_TRANSFER',
                'payment_reference': 'PAY-2024-001',
                'remarks': 'Payment processed successfully'
            }
        )
    ]
)
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
            
    except Exception:
        logger.exception(f"Error processing payment for claim {claim_id}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get claim status",
    description="Get current status and details of a claim",
    responses={
        200: ClaimStatusSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='claim_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the claim'
        )
    ]
)
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
            
    except Exception:
        logger.exception("Error getting claim status for {claim_id}")
        return Response({
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# AUDIT TRAIL API ENDPOINTS
# =============================================================================

@extend_schema(
    summary="Get audit trail",
    description="Retrieve audit trail for specified date range or user",
    responses={
        200: {'type': 'array', 'items': {'type': 'object'}},
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Start date for audit trail (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='End date for audit trail (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='user_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='User ID to filter audit trail (optional)'
        )
    ]
)
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
        
    except Exception:
        logger.exception("Error getting audit trail")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Export audit trail",
    description="Export audit trail to specified format (CSV/JSON)",
    responses={
        200: {'type': 'object', 'properties': {'export_path': {'type': 'string'}}},
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Start date for export (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='End date for export (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='format',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Export format (CSV/JSON)',
            enum=['CSV', 'JSON']
        )
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanViewAuditTrail])
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
        
        # Validate and convert dates
        try:
            from datetime import date
            start_date_obj = date.fromisoformat(start_date)
            end_date_obj = date.fromisoformat(end_date)
        except Exception:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = audit_service.export_audit_trail(start_date_obj, end_date_obj, format_type)
        
        if result['success']:
            return Response({
                'export_path': result['export_path'],
                'message': result['message'],
                'format': result['format']
            }, status=status.HTTP_200_OK)
        else:
            # Map error codes to appropriate HTTP status codes
            error_code = result.get('error_code', 'INTERNAL_ERROR')
            if error_code == 'UNSUPPORTED_FORMAT':
                return Response({
                    'error': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
            elif error_code == 'VALIDATION_ERROR':
                return Response({
                    'error': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
            else:  # INTERNAL_ERROR or unknown
                return Response({
                    'error': result['message']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception:
        logger.exception("Error exporting audit trail")
        return Response({
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# NOTIFICATION API ENDPOINTS
# =============================================================================

@extend_schema(
    summary="Send notification",
    description="Send notification to specified recipient",
    request=NotificationSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    examples=[
        OpenApiExample(
            'Email Notification',
            summary='Example email notification',
            description='Example of sending an email notification',
            value={
                'recipient': 'user@example.com',
                'message': 'Your claim has been approved',
                'notification_type': 'EMAIL',
                'priority': 'NORMAL'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanSendNotifications])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def send_notification(request):
    """Send notification to specified recipient"""
    try:
        notification_service = NotificationServiceFactory.create_notification_service()
        # Prepare parameters according to service signature: (recipient, subject, message, priority)
        recipient = request.data.get('recipient')
        message = request.data.get('message', '')
        subject = request.data.get('subject')
        notif_type = request.data.get('type')  # If provided, use as a subject prefix only
        if not subject:
            default_subject = (message[:50] if message else 'Notification')
            subject = f"[{notif_type}] {default_subject}" if notif_type else default_subject
        else:
            subject = f"[{notif_type}] {subject}" if notif_type else subject
        priority = request.data.get('priority', 'NORMAL')

        result = notification_service.send_notification(
            recipient=recipient,
            subject=subject,
            message=message,
            priority=priority
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception:
        logger.exception("Error sending notification")
        return Response({
            'success': False,
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PROVIDER MANAGEMENT API ENDPOINTS
# =============================================================================

@extend_schema(
    summary="Register provider",
    description="Register a new healthcare provider",
    request=ProviderRegistrationSerializer,
    responses={
        201: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    examples=[
        OpenApiExample(
            'Provider Registration',
            summary='Example provider registration',
            description='Example of registering a new provider',
            value={
                'hospital_reference': 'HOSP-001',
                'hospital_name': 'City General Hospital',
                'hospital_address': '123 Main Street, City',
                'contact_person': 'Dr. John Smith',
                'hospital_email': 'contact@cityhospital.com',
                'hospital_phone_number': '+1-555-0123',
                'hospital_website': 'https://cityhospital.com'
            }
        )
    ]
)
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
            
    except Exception:
        logger.exception("Error registering provider")
        return Response({
            'success': False,
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Activate provider",
    description="Activate a healthcare provider",
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='provider_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the provider'
        )
    ]
)
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
            
    except Exception:
        logger.exception("Error activating provider {provider_id}")
        return Response({
            'success': False,
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Deactivate provider",
    description="Deactivate a healthcare provider with reason",
    request=ProviderDeactivationSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='provider_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the provider'
        )
    ]
)
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
            
    except Exception:
        logger.exception("Error deactivating provider {provider_id}")
        return Response({
            'success': False,
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get provider services",
    description="Get all services available for a provider",
    responses={
        200: {'type': 'array', 'items': {'type': 'object'}},
        500: ErrorResponseSerializer
    },
    parameters=[
        OpenApiParameter(
            name='provider_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique identifier for the provider'
        )
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_provider_services(request, provider_id):
    """Get all services for a provider"""
    try:
        provider_service = ProviderManagementFactory.create_provider_management_service()
        result = provider_service.get_provider_services(provider_id)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception:
        logger.exception("Error getting provider services for {provider_id}")
        return Response({
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# REPORTING API ENDPOINTS
# =============================================================================

@extend_schema(
    summary="Get dashboard metrics",
    description="Get dashboard metrics and KPIs",
    responses={
        200: DashboardMetricsSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def get_dashboard_metrics(request):
    """Get dashboard metrics and KPIs"""
    try:
        reporting_service = ReportingEngineFactory.create_reporting_engine()
        result = reporting_service.get_dashboard_metrics()
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception:
        logger.exception("Error getting dashboard metrics")
        return Response({
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Generate report",
    description="Generate a custom report",
    request=ReportGenerationSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    examples=[
        OpenApiExample(
            'Claims Report',
            summary='Example claims report generation',
            description='Example of generating a claims report',
            value={
                'report_type': 'CLAIMS',
                'start_date': '2024-01-01',
                'end_date': '2024-01-31',
                'format_type': 'CSV'
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanGenerateReports])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def generate_report(request):
    """Generate a custom report"""
    try:
        reporting_service = ReportingEngineFactory.create_reporting_engine()
        # Validate payload via serializer
        serializer = ReportGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data

        # Map serializer choices to enums
        # Expect serializer to emit canonical strings like 'CLAIMS_SUMMARY', 'CSV', and date objects
        report_type_value = v.get('report_type')
        format_value = v.get('format_type', 'CSV')
        start_date = v.get('start_date')
        end_date = v.get('end_date')

        try:
            report_type_enum = ReportType(report_type_value)
        except Exception:
            return Response({'success': False, 'error': f"Invalid report_type '{report_type_value}'"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            format_enum = ReportFormat(format_value)
        except Exception:
            return Response({'success': False, 'error': f"Invalid format '{format_value}'"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate report data using date objects
        data = reporting_service.generate_report(report_type_enum, start_date, end_date)

        if 'error' in data:
            return Response({'success': False, 'error': data['error']}, status=status.HTTP_400_BAD_REQUEST)

        # Export/serialize according to format
        if format_enum == ReportFormat.JSON:
            return Response({'success': True, 'report': data}, status=status.HTTP_200_OK)
        else:
            filename = f"{report_type_enum.value.lower()}_{start_date}_{end_date}"
            export_path = reporting_service.export_report(data, format_enum, filename)
            return Response({'success': True, 'export_path': export_path, 'format': format_enum.value}, status=status.HTTP_200_OK)
            
    except Exception:
        logger.exception("Error generating report")
        return Response({
            'success': False,
            'error': f'Internal server error: '
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@extend_schema(
    summary="Health check",
    description="Health check endpoint for monitoring",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'example': 'healthy'},
                'service': {'type': 'string', 'example': 'HMS Ultra API'},
                'version': {'type': 'string', 'example': '1.0.0'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    return Response({
        'status': 'healthy',
        'service': 'HMS Ultra API',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
