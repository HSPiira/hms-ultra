from django.contrib import admin, messages
from django.db import transaction
from typing import Any, Optional

from core.models import Claim, ClaimDetail, ClaimPayment
from core.services.claim_workflow import ClaimWorkflowFactory


class ClaimDetailInline(admin.TabularInline):
    model = ClaimDetail
    extra = 0
    fields = (
        'service', 'quantity', 'unit_price', 'total_price',
    )
    readonly_fields = ()


class ClaimPaymentInline(admin.TabularInline):
    model = ClaimPayment
    extra = 0
    fields = (
        'payment_reference', 'payment_amount', 'payment_date',
    )
    readonly_fields = ()


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'claimform_number', 'invoice_number', 'member', 'hospital',
        'service_date', 'approved', 'hospital_claimamount', 'member_claimamount',
    )
    search_fields = (
        'claimform_number', 'invoice_number', 'member__member_name', 'hospital__hospital_name',
    )
    list_filter = (
        'approved', 'service_date', 'hospital',
    )
    inlines = [ClaimDetailInline, ClaimPaymentInline]
    list_select_related = ('member', 'hospital')

    actions = ['action_approve', 'action_reject', 'action_mark_paid']

    @transaction.atomic
    def action_approve(self, request, queryset):
        workflow = ClaimWorkflowFactory.create_claim_workflow_service()
        approver_id: str = str(request.user.id)

        success_count = 0
        errors = 0
        for claim in queryset:
            result = workflow.approve_claim(str(claim.id), approver_id)
            if result.get('success'):
                success_count += 1
            else:
                errors += 1
        if success_count:
            messages.success(request, f"Approved {success_count} claim(s).")
        if errors:
            messages.error(request, f"Failed to approve {errors} claim(s). Check logs or validation messages.")

    action_approve.short_description = "Approve selected claims"

    @transaction.atomic
    def action_reject(self, request, queryset):
        workflow = ClaimWorkflowFactory.create_claim_workflow_service()
        rejector_id: str = str(request.user.id)
        default_reason = "Rejected via admin"

        success_count = 0
        errors = 0
        for claim in queryset:
            result = workflow.reject_claim(str(claim.id), default_reason, rejector_id)
            if result.get('success'):
                success_count += 1
            else:
                errors += 1
        if success_count:
            messages.success(request, f"Rejected {success_count} claim(s).")
        if errors:
            messages.error(request, f"Failed to reject {errors} claim(s). Check logs or validation messages.")

    action_reject.short_description = "Reject selected claims (default reason)"

    @transaction.atomic
    def action_mark_paid(self, request, queryset):
        workflow = ClaimWorkflowFactory.create_claim_workflow_service()

        success_count = 0
        errors = 0
        for claim in queryset:
            payment_data = {
                'amount': claim.member_claimamount or claim.hospital_claimamount
            }
            result = workflow.pay_claim(str(claim.id), payment_data)
            if result.get('success'):
                success_count += 1
            else:
                errors += 1
        if success_count:
            messages.success(request, f"Marked {success_count} claim(s) as paid.")
        if errors:
            messages.error(request, f"Failed to mark {errors} claim(s) as paid. Check logs or validation messages.")

    action_mark_paid.short_description = "Mark selected claims as paid (use claim amount)"
