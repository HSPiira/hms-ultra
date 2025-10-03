"""
URL Configuration for HMS Ultra Core API
Defines all API endpoints and routing
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views
from .crud_views import (
    MemberViewSet, SchemeViewSet, HospitalViewSet, CompanyViewSet, CompanyTypeViewSet,
    CompanyBranchViewSet, PlanViewSet, SchemePlanViewSet, BenefitViewSet, SchemeBenefitViewSet,
    MemberDependantViewSet, HospitalBranchViewSet, HospitalDoctorViewSet, HospitalMedicineViewSet,
    HospitalServiceViewSet, HospitalLabTestViewSet, MedicineViewSet, ServiceViewSet,
    LabTestViewSet, DiagnosisViewSet, ClaimViewSet, ClaimDetailViewSet, ClaimPaymentViewSet,
    BillingSessionViewSet, DistrictViewSet, FinancialPeriodViewSet, ApplicationUserViewSet,
    ApplicationModuleViewSet, UserPermissionViewSet
)

# Create router for ViewSets
router = DefaultRouter()

# Register all CRUD ViewSets
router.register(r'members', MemberViewSet, basename='member')
router.register(r'schemes', SchemeViewSet, basename='scheme')
router.register(r'hospitals', HospitalViewSet, basename='hospital')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'company-types', CompanyTypeViewSet, basename='companytype')
router.register(r'company-branches', CompanyBranchViewSet, basename='companybranch')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'scheme-plans', SchemePlanViewSet, basename='schemeplan')
router.register(r'benefits', BenefitViewSet, basename='benefit')
router.register(r'scheme-benefits', SchemeBenefitViewSet, basename='schemebenefit')
router.register(r'member-dependants', MemberDependantViewSet, basename='memberdependant')
router.register(r'hospital-branches', HospitalBranchViewSet, basename='hospitalbranch')
router.register(r'hospital-doctors', HospitalDoctorViewSet, basename='hospitaldoctor')
router.register(r'hospital-medicines', HospitalMedicineViewSet, basename='hospitalmedicine')
router.register(r'hospital-services', HospitalServiceViewSet, basename='hospitalservice')
router.register(r'hospital-labtests', HospitalLabTestViewSet, basename='hospitallabtest')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'labtests', LabTestViewSet, basename='labtest')
router.register(r'diagnoses', DiagnosisViewSet, basename='diagnosis')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'claim-details', ClaimDetailViewSet, basename='claimdetail')
router.register(r'claim-payments', ClaimPaymentViewSet, basename='claimpayment')
router.register(r'billing-sessions', BillingSessionViewSet, basename='billingsession')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'financial-periods', FinancialPeriodViewSet, basename='financialperiod')
router.register(r'application-users', ApplicationUserViewSet, basename='applicationuser')
router.register(r'application-modules', ApplicationModuleViewSet, basename='applicationmodule')
router.register(r'user-permissions', UserPermissionViewSet, basename='userpermission')

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