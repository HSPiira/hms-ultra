from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import MemberViewSet, SchemeViewSet, HospitalViewSet, CompanyViewSet, CompanyTypeViewSet, CompanyBranchViewSet, PlanViewSet, SchemePlanViewSet, BenefitViewSet, SchemeBenefitViewSet, MemberDependantViewSet, HospitalBranchViewSet, HospitalDoctorViewSet, HospitalMedicineViewSet, HospitalServiceViewSet, HospitalLabTestViewSet, MedicineViewSet, ServiceViewSet, LabTestViewSet, DiagnosisViewSet, ClaimViewSet, ClaimDetailViewSet, ClaimPaymentViewSet, BillingSessionViewSet, DistrictViewSet, FinancialPeriodViewSet, ApplicationUserViewSet, ApplicationModuleViewSet, UserPermissionViewSet


router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'schemes', SchemeViewSet, basename='scheme')
router.register(r'hospitals', HospitalViewSet, basename='hospital')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'company-types', CompanyTypeViewSet, basename='company-type')
router.register(r'company-branches', CompanyBranchViewSet, basename='company-branch')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'scheme-plans', SchemePlanViewSet, basename='scheme-plan')
router.register(r'benefits', BenefitViewSet, basename='benefit')
router.register(r'scheme-benefits', SchemeBenefitViewSet, basename='scheme-benefit')
router.register(r'member-dependants', MemberDependantViewSet, basename='member-dependant')
router.register(r'hospital-branches', HospitalBranchViewSet, basename='hospital-branch')
router.register(r'hospital-doctors', HospitalDoctorViewSet, basename='hospital-doctor')
router.register(r'hospital-medicines', HospitalMedicineViewSet, basename='hospital-medicine')
router.register(r'hospital-services', HospitalServiceViewSet, basename='hospital-service')
router.register(r'hospital-lab-tests', HospitalLabTestViewSet, basename='hospital-lab-test')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'lab-tests', LabTestViewSet, basename='lab-test')
router.register(r'diagnoses', DiagnosisViewSet, basename='diagnosis')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'claim-details', ClaimDetailViewSet, basename='claim-detail')
router.register(r'claim-payments', ClaimPaymentViewSet, basename='claim-payment')
router.register(r'billing-sessions', BillingSessionViewSet, basename='billing-session')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'financial-periods', FinancialPeriodViewSet, basename='financial-period')
router.register(r'application-users', ApplicationUserViewSet, basename='application-user')
router.register(r'application-modules', ApplicationModuleViewSet, basename='application-module')
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permission')

urlpatterns = [
    path('', include(router.urls)),
]



