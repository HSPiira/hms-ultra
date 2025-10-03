"""
Custom Permissions for HMS Ultra
Implements role-based access control and business logic permissions
"""

from rest_framework import permissions
from django.contrib.auth.models import User
from core.models import Claim, Hospital, Member


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for admin users
        return request.user and request.user.is_staff


class IsProviderOwner(permissions.BasePermission):
    """
    Custom permission to only allow providers to access their own data.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for the provider owner or admin
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always access
        if request.user.is_staff:
            return True
        
        # Check if user is the owner of the provider (hospital)
        # Compare the created_by field with the user's username or ID
        if hasattr(obj, 'created_by') and obj.created_by:
            # If created_by stores username, compare with request.user.username
            if obj.created_by == request.user.username:
                return True
            # If created_by stores user ID, compare with request.user.id
            try:
                if obj.created_by == str(request.user.id):
                    return True
            except (ValueError, TypeError):
                pass
        
        return False


class CanApproveClaims(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to approve claims.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always approve
        if request.user.is_staff:
            return True
        
        # Check if user has specific approval permissions
        # This could be extended to check user groups or custom permissions
        return hasattr(request.user, 'can_approve_claims') and request.user.can_approve_claims


class CanProcessPayments(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to process payments.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always process payments
        if request.user.is_staff:
            return True
        
        # Check if user has specific payment processing permissions
        return hasattr(request.user, 'can_process_payments') and request.user.can_process_payments


class CanViewAuditTrail(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to view audit trails.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always view audit trails
        if request.user.is_staff:
            return True
        
        # Check if user has audit trail viewing permissions
        return hasattr(request.user, 'can_view_audit_trail') and request.user.can_view_audit_trail


class CanManageProviders(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to manage providers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always manage providers
        if request.user.is_staff:
            return True
        
        # Check if user has provider management permissions
        return hasattr(request.user, 'can_manage_providers') and request.user.can_manage_providers


class CanGenerateReports(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to generate reports.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always generate reports
        if request.user.is_staff:
            return True
        
        # Check if user has reporting permissions
        return hasattr(request.user, 'can_generate_reports') and request.user.can_generate_reports


class IsClaimOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow claim owners or admins to access claim data.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access all claims
        if request.user and request.user.is_staff:
            return True
        
        # Check if user is associated with the member's company
        if hasattr(obj, 'member') and obj.member:
            # Safely check if member exists and has a company
            if not obj.member or not hasattr(obj.member, 'company'):
                return False
            
            # Check if user has permissions to view claims for this company
            # This would typically involve checking user-company associations
            # For now, we'll check if the user has a company association
            if hasattr(request.user, 'company') and request.user.company:
                return request.user.company.id == obj.member.company.id
            
            # If no company association, deny access
            return False
        
        # Check if user is associated with the hospital
        if hasattr(obj, 'hospital') and obj.hospital:
            # This could be extended to check hospital staff associations
            return False
        
        return False


class IsProviderStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow provider staff or admins to access provider data.
    """
    def has_object_permission(self, request, view, obj):
        # Guard against None objects
        if not obj:
            return False
        
        # Anonymous users are denied
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can access all provider data
        if request.user.is_staff:
            return True
        
        # Check if user is associated with the provider (hospital)
        try:
            # Check if user is staff of this hospital
            if hasattr(obj, 'staff'):
                # If staff associations exist, check if user is staff
                if obj.staff.exists():
                    return obj.staff.filter(user=request.user, is_active=True).exists()
                else:
                    # If no staff associations exist yet, allow authenticated users
                    # This is a temporary fallback until staff associations are fully implemented
                    return True
            
            # Fallback: Check if user has provider_staff role (if implemented)
            if hasattr(request.user, 'has_role'):
                return request.user.has_role('provider_staff')
            
            # If no staff associations exist yet, allow authenticated users
            # This is a temporary fallback until staff associations are fully implemented
            return True
            
        except (AttributeError, Exception):
            # If any error occurs, deny access for safety
            return False


class CanSendNotifications(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to send notifications.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always send notifications
        if request.user.is_staff:
            return True
        
        # Check if user has notification sending permissions
        return hasattr(request.user, 'can_send_notifications') and request.user.can_send_notifications


class CanViewAuditTrail(permissions.BasePermission):
    """
    Custom permission to only allow authorized users to view audit trail data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can always view audit trails
        if request.user.is_staff:
            return True
        
        # Check if user has audit trail viewing permissions
        return hasattr(request.user, 'can_view_audit_trail') and request.user.can_view_audit_trail
