"""
Serializers for HMS Ultra API
Defines data serialization for API requests and responses
"""

from rest_framework import serializers
from core.models import Claim, Hospital, Member, Company, Service, Medicine, LabTest


class ClaimSubmissionSerializer(serializers.Serializer):
    """Serializer for claim submission"""
    member_id = serializers.CharField(max_length=27)
    hospital_id = serializers.CharField(max_length=27)
    service_date = serializers.DateField()
    claimform_number = serializers.CharField(max_length=100)
    invoice_number = serializers.CharField(max_length=100)
    hospital_claimamount = serializers.DecimalField(max_digits=15, decimal_places=2)
    created_by = serializers.CharField(max_length=100, required=False)


class ClaimApprovalSerializer(serializers.Serializer):
    """Serializer for claim approval"""
    approver_id = serializers.CharField(max_length=27)
    approval_notes = serializers.CharField(max_length=500, required=False)


class ClaimRejectionSerializer(serializers.Serializer):
    """Serializer for claim rejection"""
    reason = serializers.CharField(max_length=500)
    rejector_id = serializers.CharField(max_length=27)


class PaymentProcessingSerializer(serializers.Serializer):
    """Serializer for payment processing"""
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_method = serializers.CharField(max_length=50)
    payment_reference = serializers.CharField(max_length=100, required=False)
    remarks = serializers.CharField(max_length=500, required=False)


class ProviderRegistrationSerializer(serializers.Serializer):
    """Serializer for provider registration"""
    hospital_reference = serializers.CharField(max_length=50)
    hospital_name = serializers.CharField(max_length=200)
    hospital_address = serializers.CharField(max_length=500, required=False)
    contact_person = serializers.CharField(max_length=100, required=False)
    hospital_email = serializers.EmailField(required=False)
    hospital_phone_number = serializers.CharField(max_length=50, required=False)
    hospital_website = serializers.URLField(required=False)


class ProviderDeactivationSerializer(serializers.Serializer):
    """Serializer for provider deactivation"""
    reason = serializers.CharField(max_length=500)


class NotificationSerializer(serializers.Serializer):
    """Serializer for notification sending"""
    recipient = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
    notification_type = serializers.ChoiceField(choices=[
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification')
    ], default='EMAIL')
    priority = serializers.ChoiceField(choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ], default='NORMAL')


class ReportGenerationSerializer(serializers.Serializer):
    """Serializer for report generation"""
    report_type = serializers.ChoiceField(choices=[
        ('CLAIMS', 'Claims Report'),
        ('PROVIDERS', 'Providers Report'),
        ('MEMBERS', 'Members Report'),
        ('FINANCIAL', 'Financial Report')
    ])
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    format_type = serializers.ChoiceField(choices=[
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
        ('PDF', 'PDF')
    ], default='CSV')


class AuditTrailQuerySerializer(serializers.Serializer):
    """Serializer for audit trail queries"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    user_id = serializers.CharField(max_length=27, required=False)


class ClaimStatusSerializer(serializers.Serializer):
    """Serializer for claim status response"""
    claim_id = serializers.CharField(max_length=27)
    status = serializers.CharField(max_length=50)
    stage = serializers.CharField(max_length=50)
    submitted_date = serializers.DateTimeField()
    approved_date = serializers.CharField(max_length=200, allow_null=True)
    paid_date = serializers.CharField(max_length=200, allow_null=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    benefit_amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics response"""
    total_claims = serializers.IntegerField()
    pending_claims = serializers.IntegerField()
    approved_claims = serializers.IntegerField()
    rejected_claims = serializers.IntegerField()
    total_providers = serializers.IntegerField()
    active_providers = serializers.IntegerField()
    total_members = serializers.IntegerField()
    total_amount_claimed = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_amount_paid = serializers.DecimalField(max_digits=15, decimal_places=2)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField(max_length=500)
    details = serializers.CharField(max_length=1000, required=False)


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success responses"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(max_length=500)
    data = serializers.DictField(required=False)
