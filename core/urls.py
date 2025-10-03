"""
URL Configuration for HMS Ultra Core API
Defines all API endpoints and routing
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create router for ViewSets (if needed in future)
router = DefaultRouter()

# API URL patterns
urlpatterns = [
    # Health Check
    path('health/', api_views.health_check, name='health_check'),
    
    # Claim Workflow Endpoints
    path('claims/submit/', api_views.submit_claim, name='submit_claim'),
    path('claims/<str:claim_id>/approve/', api_views.approve_claim, name='approve_claim'),
    path('claims/<str:claim_id>/reject/', api_views.reject_claim, name='reject_claim'),
    path('claims/<str:claim_id>/payment/', api_views.process_payment, name='process_payment'),
    path('claims/<str:claim_id>/status/', api_views.get_claim_status, name='get_claim_status'),
    
    # Audit Trail Endpoints
    path('audit/trail/', api_views.get_audit_trail, name='get_audit_trail'),
    path('audit/export/', api_views.export_audit_trail, name='export_audit_trail'),
    
    # Notification Endpoints
    path('notifications/send/', api_views.send_notification, name='send_notification'),
    
    # Provider Management Endpoints
    path('providers/register/', api_views.register_provider, name='register_provider'),
    path('providers/<str:provider_id>/activate/', api_views.activate_provider, name='activate_provider'),
    path('providers/<str:provider_id>/deactivate/', api_views.deactivate_provider, name='deactivate_provider'),
    path('providers/<str:provider_id>/services/', api_views.get_provider_services, name='get_provider_services'),
    
    # Reporting Endpoints
    path('reports/dashboard/', api_views.get_dashboard_metrics, name='get_dashboard_metrics'),
    path('reports/generate/', api_views.generate_report, name='generate_report'),
]

# Include router URLs (for future ViewSets)
urlpatterns += router.urls