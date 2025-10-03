"""
OpenAPI Schema for HMS Ultra API
Defines comprehensive API documentation using drf-spectacular
"""

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from . import api_views
from .serializers import (
    ClaimSubmissionSerializer, ClaimApprovalSerializer, ClaimRejectionSerializer,
    PaymentProcessingSerializer, ProviderRegistrationSerializer, 
    ProviderDeactivationSerializer, NotificationSerializer, ReportGenerationSerializer,
    AuditTrailQuerySerializer, ClaimStatusSerializer, DashboardMetricsSerializer,
    ErrorResponseSerializer, SuccessResponseSerializer
)


# =============================================================================
# CLAIM WORKFLOW SCHEMAS
# =============================================================================

@extend_schema_view(
    post=extend_schema(
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
)
def submit_claim_schema():
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Approve a claim",
        description="Approve a submitted claim for payment processing",
        request=ClaimApprovalSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
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
)
def approve_claim_schema():
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Reject a claim",
        description="Reject a submitted claim with reason",
        request=ClaimRejectionSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
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
)
def reject_claim_schema():
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Process claim payment",
        description="Process payment for an approved claim",
        request=PaymentProcessingSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
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
)
def process_payment_schema():
    pass


@extend_schema_view(
    get=extend_schema(
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
)
def get_claim_status_schema():
    pass


# =============================================================================
# AUDIT TRAIL SCHEMAS
# =============================================================================

@extend_schema_view(
    get=extend_schema(
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
)
def get_audit_trail_schema():
    pass


@extend_schema_view(
    get=extend_schema(
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
)
def export_audit_trail_schema():
    pass


# =============================================================================
# NOTIFICATION SCHEMAS
# =============================================================================

@extend_schema_view(
    post=extend_schema(
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
)
def send_notification_schema():
    pass


# =============================================================================
# PROVIDER MANAGEMENT SCHEMAS
# =============================================================================

@extend_schema_view(
    post=extend_schema(
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
)
def register_provider_schema():
    pass


@extend_schema_view(
    post=extend_schema(
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
)
def activate_provider_schema():
    pass


@extend_schema_view(
    post=extend_schema(
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
)
def deactivate_provider_schema():
    pass


@extend_schema_view(
    get=extend_schema(
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
)
def get_provider_services_schema():
    pass


# =============================================================================
# REPORTING SCHEMAS
# =============================================================================

@extend_schema_view(
    get=extend_schema(
        summary="Get dashboard metrics",
        description="Get dashboard metrics and KPIs",
        responses={
            200: DashboardMetricsSerializer,
            500: ErrorResponseSerializer
        }
    )
)
def get_dashboard_metrics_schema():
    pass


@extend_schema_view(
    post=extend_schema(
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
)
def generate_report_schema():
    pass


# =============================================================================
# HEALTH CHECK SCHEMA
# =============================================================================

@extend_schema_view(
    get=extend_schema(
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
)
def health_check_schema():
    pass
