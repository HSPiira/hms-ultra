"""
CRUD ViewSets for HMS Ultra Core Modules
Simplified ViewSets that work directly with models and repositories
"""

from rest_framework import serializers, viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from core.models import (
    Member, Scheme, Hospital, Company, CompanyType, CompanyBranch, Plan, 
    SchemePlan, Benefit, SchemeBenefit, MemberDependant, HospitalBranch, 
    HospitalDoctor, HospitalMedicine, HospitalService, HospitalLabTest, 
    Medicine, Service, LabTest, Diagnosis, Claim, ClaimDetail, ClaimPayment, 
    BillingSession, District, FinancialPeriod, ApplicationUser, ApplicationModule, 
    UserPermission
)


# =============================================================================
# SERIALIZERS
# =============================================================================

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = '__all__'


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = '__all__'


class CompanyBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyBranch
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SchemePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemePlan
        fields = '__all__'


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = '__all__'


class SchemeBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeBenefit
        fields = '__all__'


class MemberDependantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDependant
        fields = '__all__'


class HospitalBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalBranch
        fields = '__all__'


class HospitalDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalDoctor
        fields = '__all__'


class HospitalMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalMedicine
        fields = '__all__'


class HospitalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalService
        fields = '__all__'


class HospitalLabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalLabTest
        fields = '__all__'


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = '__all__'


class ClaimDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDetail
        fields = '__all__'


class ClaimPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimPayment
        fields = '__all__'


class BillingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingSession
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class FinancialPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialPeriod
        fields = '__all__'


class ApplicationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUser
        fields = '__all__'


class ApplicationModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationModule
        fields = '__all__'


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = '__all__'


# =============================================================================
# VIEWSETS
# =============================================================================

class MemberViewSet(viewsets.ModelViewSet):
    """CRUD operations for Members"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['member_name', 'employee_id', 'national_id', 'card_number']
    ordering_fields = ['created_date', 'modified_date', 'member_name', 'card_number']
    ordering = ['-created_date']


class SchemeViewSet(viewsets.ModelViewSet):
    """CRUD operations for Schemes"""
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['scheme_name', 'scheme_code']
    ordering_fields = ['created_date', 'modified_date', 'scheme_name']
    ordering = ['-created_date']


class HospitalViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospitals"""
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hospital_name', 'hospital_reference']
    ordering_fields = ['created_date', 'modified_date', 'hospital_name']
    ordering = ['-created_date']


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD operations for Companies"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'company_code']
    ordering_fields = ['created_date', 'modified_date', 'company_name']
    ordering = ['-created_date']


class CompanyTypeViewSet(viewsets.ModelViewSet):
    """CRUD operations for Company Types"""
    queryset = CompanyType.objects.all()
    serializer_class = CompanyTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['type_name', 'type_code']
    ordering_fields = ['created_date', 'modified_date', 'type_name']
    ordering = ['-created_date']


class CompanyBranchViewSet(viewsets.ModelViewSet):
    """CRUD operations for Company Branches"""
    queryset = CompanyBranch.objects.all()
    serializer_class = CompanyBranchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['branch_name', 'branch_code']
    ordering_fields = ['created_date', 'modified_date', 'branch_name']
    ordering = ['-created_date']


class PlanViewSet(viewsets.ModelViewSet):
    """CRUD operations for Plans"""
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['plan_name', 'plan_code']
    ordering_fields = ['created_date', 'modified_date', 'plan_name']
    ordering = ['-created_date']


class SchemePlanViewSet(viewsets.ModelViewSet):
    """CRUD operations for Scheme Plans"""
    queryset = SchemePlan.objects.all()
    serializer_class = SchemePlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class BenefitViewSet(viewsets.ModelViewSet):
    """CRUD operations for Benefits"""
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['benefit_name', 'benefit_code']
    ordering_fields = ['created_date', 'modified_date', 'benefit_name']
    ordering = ['-created_date']


class SchemeBenefitViewSet(viewsets.ModelViewSet):
    """CRUD operations for Scheme Benefits"""
    queryset = SchemeBenefit.objects.all()
    serializer_class = SchemeBenefitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class MemberDependantViewSet(viewsets.ModelViewSet):
    """CRUD operations for Member Dependants"""
    queryset = MemberDependant.objects.all()
    serializer_class = MemberDependantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['dependant_name', 'relationship']
    ordering_fields = ['created_date', 'modified_date', 'dependant_name']
    ordering = ['-created_date']


class HospitalBranchViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospital Branches"""
    queryset = HospitalBranch.objects.all()
    serializer_class = HospitalBranchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['branch_name', 'branch_code']
    ordering_fields = ['created_date', 'modified_date', 'branch_name']
    ordering = ['-created_date']


class HospitalDoctorViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospital Doctors"""
    queryset = HospitalDoctor.objects.all()
    serializer_class = HospitalDoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['doctor_name', 'specialization']
    ordering_fields = ['created_date', 'modified_date', 'doctor_name']
    ordering = ['-created_date']


class HospitalMedicineViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospital Medicines"""
    queryset = HospitalMedicine.objects.all()
    serializer_class = HospitalMedicineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class HospitalServiceViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospital Services"""
    queryset = HospitalService.objects.all()
    serializer_class = HospitalServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class HospitalLabTestViewSet(viewsets.ModelViewSet):
    """CRUD operations for Hospital Lab Tests"""
    queryset = HospitalLabTest.objects.all()
    serializer_class = HospitalLabTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class MedicineViewSet(viewsets.ModelViewSet):
    """CRUD operations for Medicines"""
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medicine_name', 'medicine_code']
    ordering_fields = ['created_date', 'modified_date', 'medicine_name']
    ordering = ['-created_date']


class ServiceViewSet(viewsets.ModelViewSet):
    """CRUD operations for Services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_name', 'service_code']
    ordering_fields = ['created_date', 'modified_date', 'service_name']
    ordering = ['-created_date']


class LabTestViewSet(viewsets.ModelViewSet):
    """CRUD operations for Lab Tests"""
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['test_name', 'test_code']
    ordering_fields = ['created_date', 'modified_date', 'test_name']
    ordering = ['-created_date']


class DiagnosisViewSet(viewsets.ModelViewSet):
    """CRUD operations for Diagnoses"""
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['diagnosis_name', 'diagnosis_code']
    ordering_fields = ['created_date', 'modified_date', 'diagnosis_name']
    ordering = ['-created_date']


class ClaimViewSet(viewsets.ModelViewSet):
    """CRUD operations for Claims"""
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['claimform_number', 'invoice_number']
    ordering_fields = ['created_date', 'modified_date', 'submission_date']
    ordering = ['-created_date']


class ClaimDetailViewSet(viewsets.ModelViewSet):
    """CRUD operations for Claim Details"""
    queryset = ClaimDetail.objects.all()
    serializer_class = ClaimDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']


class ClaimPaymentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Claim Payments"""
    queryset = ClaimPayment.objects.all()
    serializer_class = ClaimPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date', 'payment_date']
    ordering = ['-created_date']


class BillingSessionViewSet(viewsets.ModelViewSet):
    """CRUD operations for Billing Sessions"""
    queryset = BillingSession.objects.all()
    serializer_class = BillingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['session_name', 'session_code']
    ordering_fields = ['created_date', 'modified_date', 'session_date']
    ordering = ['-created_date']


class DistrictViewSet(viewsets.ModelViewSet):
    """CRUD operations for Districts"""
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['district_name', 'district_code']
    ordering_fields = ['created_date', 'modified_date', 'district_name']
    ordering = ['-created_date']


class FinancialPeriodViewSet(viewsets.ModelViewSet):
    """CRUD operations for Financial Periods"""
    queryset = FinancialPeriod.objects.all()
    serializer_class = FinancialPeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date', 'period_start']
    ordering = ['-created_date']


class ApplicationUserViewSet(viewsets.ModelViewSet):
    """CRUD operations for Application Users"""
    queryset = ApplicationUser.objects.all()
    serializer_class = ApplicationUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_date', 'modified_date', 'username']
    ordering = ['-created_date']


class ApplicationModuleViewSet(viewsets.ModelViewSet):
    """CRUD operations for Application Modules"""
    queryset = ApplicationModule.objects.all()
    serializer_class = ApplicationModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['module_name', 'module_code']
    ordering_fields = ['created_date', 'modified_date', 'module_name']
    ordering = ['-created_date']


class UserPermissionViewSet(viewsets.ModelViewSet):
    """CRUD operations for User Permissions"""
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_date', 'modified_date']
    ordering = ['-created_date']
