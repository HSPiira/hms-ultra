from __future__ import annotations

from dataclasses import asdict
from typing import Any

from rest_framework import serializers, viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Member, Scheme, Hospital, Company, CompanyType, CompanyBranch, Plan, SchemePlan, Benefit, SchemeBenefit, MemberDependant, HospitalBranch, HospitalDoctor, HospitalMedicine, HospitalService, HospitalLabTest, Medicine, Service, LabTest, Diagnosis, Claim, ClaimDetail, ClaimPayment, BillingSession, District, FinancialPeriod, ApplicationUser, ApplicationModule, UserPermission
from core.utils.repositories import DjangoMemberRepository, DjangoSchemeRepository, DjangoHospitalRepository, DjangoCompanyRepository, DjangoCompanyTypeRepository, DjangoCompanyBranchRepository, DjangoPlanRepository, DjangoSchemePlanRepository, DjangoBenefitRepository, DjangoSchemeBenefitRepository, DjangoMemberDependantRepository, DjangoHospitalBranchRepository, DjangoHospitalDoctorRepository, DjangoHospitalMedicineRepository, DjangoHospitalServiceRepository, DjangoHospitalLabTestRepository, DjangoMedicineRepository, DjangoServiceRepository, DjangoLabTestRepository, DjangoDiagnosisRepository, DjangoClaimRepository, DjangoClaimDetailRepository, DjangoClaimPaymentRepository, DjangoBillingSessionRepository, DjangoDistrictRepository, DjangoFinancialPeriodRepository, DjangoApplicationUserRepository, DjangoApplicationModuleRepository, DjangoUserPermissionRepository
# Services will be implemented later - using repositories directly for now


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "id",
            "company",
            "scheme",
            "member_name",
            "employee_id",
            "national_id",
            "gender",
            "date_of_birth",
            "marital_status",
            "blood_group",
            "postal_address",
            "physical_address",
            "phone_home",
            "phone_mobile",
            "email",
            "emergency_contact",
            "emergency_phone",
            "card_number",
            "date_of_joining",
            "date_of_leaving",
            "member_status",
            "photo_path",
            "created_date",
            "modified_date",
        ]

    def validate_card_number(self, value: str):
        if not value:
            return value
        qs = Member.objects.filter(card_number=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Card number already in use")
        return value


class MemberViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "created_date",
        "modified_date",
        "member_name",
        "card_number",
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = DjangoMemberRepository()
        self.service = MemberService(self.repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        ordering = request.query_params.get("ordering")
        # Optional filtering by company or scheme
        company = request.query_params.get("company")
        scheme = request.query_params.get("scheme")
        if company or scheme:
            qs = Member.objects.select_related("company", "scheme").all()
            if company:
                qs = qs.filter(company_id=company)
            if scheme:
                qs = qs.filter(scheme_id=scheme)
            if search:
                qs = qs.filter(member_name__icontains=search)
            if ordering:
                qs = qs.order_by(ordering)
            total = qs.count()
            data = MemberSerializer(qs[offset: offset + limit], many=True).data
            return Response({"count": total, "results": data})
        items, total = self.service.list_members(search=search, limit=limit, offset=offset)
        data = MemberSerializer(items, many=True).data
        return Response({"count": total, "results": data})

    def retrieve(self, request, pk: str = None):
        member = self.repo.get_by_id(pk)
        if not member:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(MemberSerializer(member).data)

    def create(self, request):
        serializer = MemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = MemberCreateDTO(
            member_name=serializer.validated_data["member_name"],
            company_id=str(serializer.validated_data["company"].id),
            scheme_id=str(serializer.validated_data["scheme"].id),
            employee_id=serializer.validated_data.get("employee_id", ""),
            national_id=serializer.validated_data.get("national_id", ""),
            gender=serializer.validated_data.get("gender", ""),
            phone_mobile=serializer.validated_data.get("phone_mobile", ""),
            email=serializer.validated_data.get("email", ""),
            card_number=serializer.validated_data.get("card_number", ""),
        )
        member = self.service.create_member(dto)
        return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = MemberSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dto = MemberUpdateDTO(
            member_name=serializer.validated_data.get("member_name"),
            employee_id=serializer.validated_data.get("employee_id"),
            national_id=serializer.validated_data.get("national_id"),
            gender=serializer.validated_data.get("gender"),
            phone_mobile=serializer.validated_data.get("phone_mobile"),
            email=serializer.validated_data.get("email"),
        )
        member = self.service.update_member(pk, dto)
        return Response(MemberSerializer(member).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk: str = None):
        member = self.service.activate_member(pk)
        return Response(MemberSerializer(member).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk: str = None):
        member = self.service.deactivate_member(pk)
        return Response(MemberSerializer(member).data)


class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = [
            "id",
            "scheme_name",
            "description",
            "limit_value",
            "company",
            "familystatus",
            "beginningdate",
            "endingdate",
            "terminationdate",
            "termination",
            "numberofdays",
            "card_code",
            "created_date",
            "modified_date",
        ]


class SchemeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoSchemeRepository()
    service = SchemeService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        company = request.query_params.get("company")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, company_id=company)
        return Response({"count": total, "results": SchemeSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(SchemeSerializer(obj).data)

    def create(self, request):
        serializer = SchemeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            scheme_name=serializer.validated_data["scheme_name"],
            company_id=str(serializer.validated_data["company"].id),
            beginningdate=str(serializer.validated_data["beginningdate"]),
            endingdate=str(serializer.validated_data["endingdate"]),
            description=serializer.validated_data.get("description", ""),
        )
        return Response(SchemeSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = SchemeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(SchemeSerializer(obj).data)


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = [
            "id",
            "hospital_reference",
            "hospital_name",
            "hospital_address",
            "contact_person",
            "outpatient_capacity",
            "inpatient_capacity",
            "district_id",
            "hospital_email",
            "hospital_website",
            "hospital_remarks",
            "hospital_phone_number",
            "outorinpatient",
            "dental",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_hospital_reference(self, value: str):
        qs = Hospital.objects.filter(hospital_reference=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("hospital_reference already exists")
        return value


class HospitalViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalRepository()
    service = HospitalService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": HospitalSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalSerializer(obj).data)

    def create(self, request):
        serializer = HospitalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_reference=serializer.validated_data["hospital_reference"],
            hospital_name=serializer.validated_data["hospital_name"],
            hospital_address=serializer.validated_data.get("hospital_address", ""),
            contact_person=serializer.validated_data.get("contact_person", ""),
            hospital_phone_number=serializer.validated_data.get("hospital_phone_number", ""),
        )
        return Response(HospitalSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalSerializer(obj).data)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "company_name",
            "contact_person",
            "company_address",
            "phone_number",
            "email",
            "website",
            "remarks",
            "location",
            "district_id",
            "currentupdate",
            "company_type",
            "created_date",
            "modified_date",
        ]

    def validate_company_name(self, value: str):
        qs = Company.objects.filter(company_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("company_name already exists")
        return value


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoCompanyRepository()
    service = CompanyService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": CompanySerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanySerializer(obj).data)

    def create(self, request):
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            company_name=serializer.validated_data["company_name"],
            contact_person=serializer.validated_data.get("contact_person", ""),
            company_address=serializer.validated_data.get("company_address", ""),
            phone_number=serializer.validated_data.get("phone_number", ""),
            email=serializer.validated_data.get("email", ""),
            website=serializer.validated_data.get("website", ""),
        )
        return Response(CompanySerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = CompanySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(CompanySerializer(obj).data)


class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = [
            "id",
            "type_name",
            "description",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_type_name(self, value: str):
        qs = CompanyType.objects.filter(type_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("type_name already exists")
        return value


class CompanyTypeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoCompanyTypeRepository()
    service = CompanyTypeService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": CompanyTypeSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanyTypeSerializer(obj).data)

    def create(self, request):
        serializer = CompanyTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            type_name=serializer.validated_data["type_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(CompanyTypeSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = CompanyTypeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(CompanyTypeSerializer(obj).data)


class CompanyBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyBranch
        fields = [
            "id",
            "branch_name",
            "company",
            "branch_address",
            "contact_person",
            "phone_number",
            "email",
            "status",
            "created_date",
            "modified_date",
        ]


class CompanyBranchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoCompanyBranchRepository()
    service = CompanyBranchService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        company = request.query_params.get("company")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, company_id=company)
        return Response({"count": total, "results": CompanyBranchSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanyBranchSerializer(obj).data)

    def create(self, request):
        serializer = CompanyBranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            branch_name=serializer.validated_data["branch_name"],
            company_id=str(serializer.validated_data["company"].id),
            branch_address=serializer.validated_data.get("branch_address", ""),
            contact_person=serializer.validated_data.get("contact_person", ""),
            phone_number=serializer.validated_data.get("phone_number", ""),
            email=serializer.validated_data.get("email", ""),
        )
        return Response(CompanyBranchSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = CompanyBranchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(CompanyBranchSerializer(obj).data)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "planname",
            "description",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_plan_name(self, value: str):
        qs = Plan.objects.filter(plan_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("plan_name already exists")
        return value


class PlanViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoPlanRepository()
    service = PlanService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": PlanSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PlanSerializer(obj).data)

    def create(self, request):
        serializer = PlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            plan_name=serializer.validated_data["plan_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(PlanSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = PlanSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(PlanSerializer(obj).data)


class SchemePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemePlan
        fields = [
            "id",
            "scheme",
            "plan",
            "status",
            "created_date",
            "modified_date",
        ]


class SchemePlanViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoSchemePlanRepository()
    service = SchemePlanService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        scheme = request.query_params.get("scheme")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, scheme_id=scheme)
        return Response({"count": total, "results": SchemePlanSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(SchemePlanSerializer(obj).data)

    def create(self, request):
        serializer = SchemePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            scheme_id=str(serializer.validated_data["scheme"].id),
            plan_id=str(serializer.validated_data["plan"].id),
        )
        return Response(SchemePlanSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = SchemePlanSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(SchemePlanSerializer(obj).data)


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = [
            "id",
            "service_name",
            "in_or_out_patient",
            "limit_amount",
            "scheme_duration",
            "remarks",
            "covered",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_service_name(self, value: str):
        qs = Benefit.objects.filter(service_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("service_name already exists")
        return value


class BenefitViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoBenefitRepository()
    service = BenefitService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": BenefitSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BenefitSerializer(obj).data)

    def create(self, request):
        serializer = BenefitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            benefit_name=serializer.validated_data["benefit_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(BenefitSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = BenefitSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(BenefitSerializer(obj).data)


class SchemeBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeBenefit
        fields = [
            "id",
            "scheme",
            "scheme_benefit",
            "limit_amount",
            "copayment_percent",
            "waiting_period_days",
            "status",
            "created_date",
            "modified_date",
        ]


class SchemeBenefitViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoSchemeBenefitRepository()
    service = SchemeBenefitService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        scheme = request.query_params.get("scheme")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, scheme_id=scheme)
        return Response({"count": total, "results": SchemeBenefitSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(SchemeBenefitSerializer(obj).data)

    def create(self, request):
        serializer = SchemeBenefitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            scheme_id=str(serializer.validated_data["scheme"].id),
            benefit_id=str(serializer.validated_data["benefit"].id),
        )
        return Response(SchemeBenefitSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = SchemeBenefitSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(SchemeBenefitSerializer(obj).data)


class MemberDependantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDependant
        fields = [
            "id",
            "member",
            "dependant_name",
            "gender",
            "dateofbirth",
            "relationship",
            "bloodgroup",
            "postal_address",
            "telhome",
            "telmobile",
            "nextofkin",
            "depcardno",
            "status",
            "dateformrecieved",
            "datephotorecieved",
            "datecardrecieved",
            "datephotosenttoinsurer",
            "datecardsenttoclient",
            "cardorphotocomment",
            "cardstatus",
            "photostatus",
            "dateofjoining",
            "dateofleaving",
            "dateofstate",
            "dateofend",
            "dimage",
            "created_date",
            "modified_date",
        ]


class MemberDependantViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoMemberDependantRepository()
    service = MemberDependantService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        member = request.query_params.get("member")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, member_id=member)
        return Response({"count": total, "results": MemberDependantSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(MemberDependantSerializer(obj).data)

    def create(self, request):
        serializer = MemberDependantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            member_id=str(serializer.validated_data["member"].id),
            dependant_name=serializer.validated_data["dependant_name"],
            relationship=serializer.validated_data.get("relationship", ""),
            date_of_birth=serializer.validated_data.get("date_of_birth"),
            gender=serializer.validated_data.get("gender", ""),
            phone_mobile=serializer.validated_data.get("phone_mobile", ""),
            email=serializer.validated_data.get("email", ""),
            national_id=serializer.validated_data.get("national_id", ""),
        )
        return Response(MemberDependantSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = MemberDependantSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(MemberDependantSerializer(obj).data)


class HospitalBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalBranch
        fields = [
            "id",
            "hospital",
            "hospital_branchname",
            "branch_address",
            "contact_person",
            "phone_number",
            "email",
            "status",
            "created_date",
            "modified_date",
        ]


class HospitalBranchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalBranchRepository()
    service = HospitalBranchService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        hospital = request.query_params.get("hospital")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, hospital_id=hospital)
        return Response({"count": total, "results": HospitalBranchSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalBranchSerializer(obj).data)

    def create(self, request):
        serializer = HospitalBranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_id=str(serializer.validated_data["hospital"].id),
            branch_name=serializer.validated_data["branch_name"],
            branch_address=serializer.validated_data.get("branch_address", ""),
            contact_person=serializer.validated_data.get("contact_person", ""),
            phone_number=serializer.validated_data.get("phone_number", ""),
            email=serializer.validated_data.get("email", ""),
        )
        return Response(HospitalBranchSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalBranchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalBranchSerializer(obj).data)


class HospitalDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalDoctor
        fields = [
            "id",
            "hospital",
            "doctorname",
            "specialization",
            "license_number",
            "qualification",
            "phone_number",
            "email",
            "status",
            "created_date",
            "modified_date",
        ]


class HospitalDoctorViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalDoctorRepository()
    service = HospitalDoctorService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        hospital = request.query_params.get("hospital")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, hospital_id=hospital)
        return Response({"count": total, "results": HospitalDoctorSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalDoctorSerializer(obj).data)

    def create(self, request):
        serializer = HospitalDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_id=str(serializer.validated_data["hospital"].id),
            doctor_name=serializer.validated_data["doctor_name"],
            specialization=serializer.validated_data.get("specialization", ""),
            phone_number=serializer.validated_data.get("phone_number", ""),
            email=serializer.validated_data.get("email", ""),
        )
        return Response(HospitalDoctorSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalDoctorSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalDoctorSerializer(obj).data)


class HospitalMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalMedicine
        fields = [
            "id",
            "hospital",
            "medicine",
            "unit_price",
            "available",
            "effective_date",
            "status",
            "created_date",
            "modified_date",
        ]


class HospitalMedicineViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalMedicineRepository()
    service = HospitalMedicineService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        hospital = request.query_params.get("hospital")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, hospital_id=hospital)
        return Response({"count": total, "results": HospitalMedicineSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalMedicineSerializer(obj).data)

    def create(self, request):
        serializer = HospitalMedicineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_id=str(serializer.validated_data["hospital"].id),
            medicine_id=str(serializer.validated_data["medicine"].id),
        )
        return Response(HospitalMedicineSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalMedicineSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalMedicineSerializer(obj).data)


class HospitalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalService
        fields = [
            "id",
            "hospital",
            "service",
            "amount",
            "available",
            "effective_date",
            "status",
            "created_date",
            "modified_date",
        ]


class HospitalServiceViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalServiceRepository()
    service = HospitalServiceService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        hospital = request.query_params.get("hospital")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, hospital_id=hospital)
        return Response({"count": total, "results": HospitalServiceSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalServiceSerializer(obj).data)

    def create(self, request):
        serializer = HospitalServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_id=str(serializer.validated_data["hospital"].id),
            service_id=str(serializer.validated_data["service"].id),
        )
        return Response(HospitalServiceSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalServiceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalServiceSerializer(obj).data)


class HospitalLabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalLabTest
        fields = [
            "id",
            "hospital",
            "labtest",
            "amount",
            "available",
            "turnaround_hours",
            "effective_date",
            "status",
            "created_date",
            "modified_date",
        ]


class HospitalLabTestViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoHospitalLabTestRepository()
    service = HospitalLabTestService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        hospital = request.query_params.get("hospital")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, hospital_id=hospital)
        return Response({"count": total, "results": HospitalLabTestSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalLabTestSerializer(obj).data)

    def create(self, request):
        serializer = HospitalLabTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            hospital_id=str(serializer.validated_data["hospital"].id),
            lab_test_id=str(serializer.validated_data["lab_test"].id),
        )
        return Response(HospitalLabTestSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = HospitalLabTestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(HospitalLabTestSerializer(obj).data)


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            "id",
            "medicineid",
            "medicinereferenceno",
            "medicinename",
            "dosageform",
            "unitprice",
            "unitsinstock",
            "reorderlevel",
            "additionalnotes",
            "dosage",
            "route",
            "duration",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_medicinename(self, value: str):
        qs = Medicine.objects.filter(medicinename=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("medicinename already exists")
        return value


class MedicineViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoMedicineRepository()
    service = MedicineService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": MedicineSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(MedicineSerializer(obj).data)

    def create(self, request):
        serializer = MedicineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            medicine_name=serializer.validated_data["medicine_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(MedicineSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = MedicineSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(MedicineSerializer(obj).data)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "service_code",
            "service_name",
            "service_category",
            "description",
            "base_amount",
            "service_type",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_service_name(self, value: str):
        qs = Service.objects.filter(service_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("service_name already exists")
        return value


class ServiceViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoServiceRepository()
    service = ServiceService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": ServiceSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ServiceSerializer(obj).data)

    def create(self, request):
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            service_name=serializer.validated_data["service_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(ServiceSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ServiceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ServiceSerializer(obj).data)


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = [
            "id",
            "test_code",
            "test_name",
            "test_category",
            "description",
            "base_amount",
            "normal_range",
            "units",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_test_name(self, value: str):
        qs = LabTest.objects.filter(test_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("test_name already exists")
        return value


class LabTestViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoLabTestRepository()
    service = LabTestService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": LabTestSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(LabTestSerializer(obj).data)

    def create(self, request):
        serializer = LabTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            test_name=serializer.validated_data["test_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(LabTestSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = LabTestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(LabTestSerializer(obj).data)


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = [
            "id",
            "icd10_code",
            "who_short_descr",
            "who_full_descr",
            "icd_3code",
            "icd_3code_desc",
            "chronicflag",
            "group_code",
            "group_description",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_icd10_code(self, value: str):
        qs = Diagnosis.objects.filter(icd10_code=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("icd10_code already exists")
        return value


class DiagnosisViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoDiagnosisRepository()
    service = DiagnosisService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": DiagnosisSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DiagnosisSerializer(obj).data)

    def create(self, request):
        serializer = DiagnosisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            diagnosis_name=serializer.validated_data["diagnosis_name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(DiagnosisSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = DiagnosisSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(DiagnosisSerializer(obj).data)


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = [
            "id",
            "transid",
            "member",
            "member_name",
            "cardno",
            "dependant",
            "dependant_name",
            "transaction_date",
            "doctor",
            "doctorname",
            "hospital",
            "hospital_name",
            "hospital_branch",
            "hospital_branchname",
            "service_date",
            "servicetype",
            "outorinpatienttransaction",
            "hospital_claimamount",
            "member_claimamount",
            "amountpaid",
            "invoice_number",
            "claimform_number",
            "claimref",
            "claimformserialnumber",
            "dateofsubmission",
            "claimformcomments",
            "claimquarantine",
            "approved",
            "lateclaimform",
            "billingsessionid",
            "chequenumbers",
            "transpaid",
            "transaction_status",
            "username",
            "created_date",
            "modified_date",
        ]

    def validate_transid(self, value: int):
        if value:
            qs = Claim.objects.filter(transid=value)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("transid already exists")
        return value


class ClaimViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoClaimRepository()
    service = ClaimService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        member = request.query_params.get("member")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, member_id=member)
        return Response({"count": total, "results": ClaimSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClaimSerializer(obj).data)

    def create(self, request):
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            member_id=str(serializer.validated_data["member"].id),
            hospital_id=str(serializer.validated_data["hospital"].id),
            claim_number=serializer.validated_data["claim_number"],
            claim_date=serializer.validated_data.get("claim_date"),
            admission_date=serializer.validated_data.get("admission_date"),
            discharge_date=serializer.validated_data.get("discharge_date"),
            total_amount=serializer.validated_data.get("total_amount", 0.0),
        )
        return Response(ClaimSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ClaimSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ClaimSerializer(obj).data)


class ClaimDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDetail
        fields = [
            "id",
            "claim",
            "transid",
            "transaction_date",
            "trans_type",
            "item_code",
            "description",
            "unit_price",
            "quantity",
            "total_amount",
            "comments",
            "status",
            "allowed",
            "chronic",
            "created_date",
            "modified_date",
        ]


class ClaimDetailViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoClaimDetailRepository()
    service = ClaimDetailService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        claim = request.query_params.get("claim")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, claim_id=claim)
        return Response({"count": total, "results": ClaimDetailSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClaimDetailSerializer(obj).data)

    def create(self, request):
        serializer = ClaimDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            claim_id=str(serializer.validated_data["claim"].id),
            description=serializer.validated_data["description"],
            amount=serializer.validated_data.get("amount", 0.0),
            quantity=serializer.validated_data.get("quantity", 1),
            unit_price=serializer.validated_data.get("unit_price", 0.0),
        )
        return Response(ClaimDetailSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ClaimDetailSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ClaimDetailSerializer(obj).data)


class ClaimPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimPayment
        fields = [
            "id",
            "claim",
            "hospital",
            "payment_amount",
            "payment_date",
            "payment_method",
            "payment_reference",
            "cheque_number",
            "bank_name",
            "payment_status",
            "remarks",
            "created_by",
            "created_date",
            "modified_date",
        ]


class ClaimPaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoClaimPaymentRepository()
    service = ClaimPaymentService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        claim = request.query_params.get("claim")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, claim_id=claim)
        return Response({"count": total, "results": ClaimPaymentSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClaimPaymentSerializer(obj).data)

    def create(self, request):
        serializer = ClaimPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            claim_id=str(serializer.validated_data["claim"].id),
            payment_reference=serializer.validated_data["payment_reference"],
            amount=serializer.validated_data["amount"],
            payment_date=serializer.validated_data.get("payment_date"),
            payment_method=serializer.validated_data.get("payment_method", ""),
        )
        return Response(ClaimPaymentSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ClaimPaymentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ClaimPaymentSerializer(obj).data)


class BillingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingSession
        fields = [
            "id",
            "session_name",
            "session_date",
            "from_date",
            "to_date",
            "total_claims",
            "total_amount",
            "session_status",
            "created_by",
            "created_date",
            "modified_date",
        ]

    def validate_session_name(self, value: str):
        if value:
            qs = BillingSession.objects.filter(session_name=value)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("session_name already exists")
        return value


class BillingSessionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoBillingSessionRepository()
    service = BillingSessionService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": BillingSessionSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BillingSessionSerializer(obj).data)

    def create(self, request):
        serializer = BillingSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            session_name=serializer.validated_data["session_name"],
            session_date=serializer.validated_data.get("session_date"),
        )
        return Response(BillingSessionSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = BillingSessionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(BillingSessionSerializer(obj).data)


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = [
            "id",
            "district_name",
            "region",
            "country_code",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_district_name(self, value: str):
        qs = District.objects.filter(district_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("district_name already exists")
        return value


class DistrictViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoDistrictRepository()
    service = DistrictService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": DistrictSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DistrictSerializer(obj).data)

    def create(self, request):
        serializer = DistrictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            district_name=serializer.validated_data["district_name"],
            district_code=serializer.validated_data.get("district_code", ""),
        )
        return Response(DistrictSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = DistrictSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(DistrictSerializer(obj).data)


class FinancialPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialPeriod
        fields = [
            "id",
            "period_name",
            "start_date",
            "end_date",
            "is_current",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_period_name(self, value: str):
        if value:
            qs = FinancialPeriod.objects.filter(period_name=value)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("period_name already exists")
        return value


class FinancialPeriodViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoFinancialPeriodRepository()
    service = FinancialPeriodService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": FinancialPeriodSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(FinancialPeriodSerializer(obj).data)

    def create(self, request):
        serializer = FinancialPeriodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            period_name=serializer.validated_data["period_name"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
        )
        return Response(FinancialPeriodSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = FinancialPeriodSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(FinancialPeriodSerializer(obj).data)


class ApplicationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUser
        fields = [
            "id",
            "empid",
            "username",
            "password",
            "lastlogin",
            "updatedate",
            "account_status",
            "password_expires",
            "failed_attempts",
            "created_date",
            "modified_date",
        ]

    def validate_username(self, value: str):
        qs = ApplicationUser.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("username already exists")
        return value


class ApplicationUserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoApplicationUserRepository()
    service = ApplicationUserService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": ApplicationUserSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ApplicationUserSerializer(obj).data)

    def create(self, request):
        serializer = ApplicationUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            username=serializer.validated_data["username"],
            email=serializer.validated_data.get("email", ""),
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            is_active=serializer.validated_data.get("is_active", True),
            is_staff=serializer.validated_data.get("is_staff", False),
        )
        return Response(ApplicationUserSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ApplicationUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ApplicationUserSerializer(obj).data)


class ApplicationModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationModule
        fields = [
            "id",
            "module_code",
            "module_name",
            "description",
            "parent_module_id",
            "module_order",
            "status",
            "created_date",
            "modified_date",
        ]

    def validate_module_name(self, value: str):
        qs = ApplicationModule.objects.filter(module_name=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("module_name already exists")
        return value


class ApplicationModuleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoApplicationModuleRepository()
    service = ApplicationModuleService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset)
        return Response({"count": total, "results": ApplicationModuleSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ApplicationModuleSerializer(obj).data)

    def create(self, request):
        serializer = ApplicationModuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            module_name=serializer.validated_data["module_name"],
            module_description=serializer.validated_data.get("module_description", ""),
            module_url=serializer.validated_data.get("module_url", ""),
        )
        return Response(ApplicationModuleSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = ApplicationModuleSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(ApplicationModuleSerializer(obj).data)


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = [
            "id",
            "user",
            "module",
            "can_view",
            "can_create",
            "can_edit",
            "can_delete",
            "can_approve",
            "granted_by",
            "granted_date",
            "created_date",
            "modified_date",
        ]


class UserPermissionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    repo = DjangoUserPermissionRepository()
    service = UserPermissionService(repo)

    def list(self, request):
        search = request.query_params.get("search")
        user = request.query_params.get("user")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        items, total = self.service.list(search=search, limit=limit, offset=offset, user_id=user)
        return Response({"count": total, "results": UserPermissionSerializer(items, many=True).data})

    def retrieve(self, request, pk: str = None):
        obj = self.repo.get_by_id(pk)
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserPermissionSerializer(obj).data)

    def create(self, request):
        serializer = UserPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create(
            user_id=str(serializer.validated_data["user"].id),
            module_id=str(serializer.validated_data["module"].id),
            permission_name=serializer.validated_data["permission_name"],
            permission_description=serializer.validated_data.get("permission_description", ""),
        )
        return Response(UserPermissionSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk: str = None):
        serializer = UserPermissionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update(pk, **serializer.validated_data)
        return Response(UserPermissionSerializer(obj).data)

