"""
Custom Permissions for HMS Ultra
Implements role-based access control and business logic permissions
"""

from rest_framework import permissions
from django.contrib.auth.models import User
from .models import Claim, Hospital, Member


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
        return (request.user and request.user.is_authenticated and 
                (request.user.is_staff or obj.id == request.user.id))


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
        
        # Check if user is the claim owner (member)
        if hasattr(obj, 'member') and obj.member:
            return request.user and request.user.id == obj.member.user.id
        
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
        # Admin users can access all provider data
        if request.user and request.user.is_staff:
            return True
        
        # Check if user is associated with the provider
        # This could be extended to check hospital staff associations
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
