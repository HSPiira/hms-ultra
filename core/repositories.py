from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Protocol, Iterable, Tuple

from django.db.models import QuerySet

from .models import Member, Scheme, Hospital, Company, CompanyType, CompanyBranch, Plan, SchemePlan, Benefit, SchemeBenefit, MemberDependant, HospitalBranch, HospitalDoctor, HospitalMedicine, HospitalService, HospitalLabTest, Medicine, Service, LabTest, Diagnosis, Claim, ClaimDetail, ClaimPayment, BillingSession, District, FinancialPeriod, ApplicationUser, ApplicationModule, UserPermission


class MemberRepository(ABC):
    @abstractmethod
    def get_by_id(self, member_id: str) -> Optional[Member]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Member], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Member:
        raise NotImplementedError

    @abstractmethod
    def update(self, member: Member, **attrs) -> Member:
        raise NotImplementedError


class DjangoMemberRepository(MemberRepository):
    def get_by_id(self, member_id: str) -> Optional[Member]:
        try:
            return Member.objects.select_related("company", "scheme").get(id=member_id)
        except Member.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Member], int]:
        qs: QuerySet[Member] = Member.objects.select_related("company", "scheme").all().order_by("-created_date")
        if search:
            qs = qs.filter(member_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Member:
        return Member.objects.create(**attrs)

    def update(self, member: Member, **attrs) -> Member:
        for key, value in attrs.items():
            setattr(member, key, value)
        member.save(update_fields=list(attrs.keys()))
        return member


class SchemeRepository(ABC):
    @abstractmethod
    def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None) -> Tuple[Iterable[Scheme], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Scheme:
        raise NotImplementedError

    @abstractmethod
    def update(self, scheme: Scheme, **attrs) -> Scheme:
        raise NotImplementedError


class DjangoSchemeRepository(SchemeRepository):
    def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        try:
            return Scheme.objects.select_related("company").get(id=scheme_id)
        except Scheme.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None) -> Tuple[Iterable[Scheme], int]:
        qs: QuerySet[Scheme] = Scheme.objects.select_related("company").all().order_by("-created_date")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if search:
            qs = qs.filter(scheme_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Scheme:
        return Scheme.objects.create(**attrs)

    def update(self, scheme: Scheme, **attrs) -> Scheme:
        for k, v in attrs.items():
            setattr(scheme, k, v)
        scheme.save(update_fields=list(attrs.keys()))
        return scheme


class HospitalRepository(ABC):
    @abstractmethod
    def get_by_id(self, hospital_id: str) -> Optional[Hospital]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Hospital], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Hospital:
        raise NotImplementedError

    @abstractmethod
    def update(self, hospital: Hospital, **attrs) -> Hospital:
        raise NotImplementedError


class DjangoHospitalRepository(HospitalRepository):
    def get_by_id(self, hospital_id: str) -> Optional[Hospital]:
        try:
            return Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Hospital], int]:
        qs: QuerySet[Hospital] = Hospital.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(hospital_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Hospital:
        return Hospital.objects.create(**attrs)

    def update(self, hospital: Hospital, **attrs) -> Hospital:
        for k, v in attrs.items():
            setattr(hospital, k, v)
        hospital.save(update_fields=list(attrs.keys()))
        return hospital


class CompanyRepository(ABC):
    @abstractmethod
    def get_by_id(self, company_id: str) -> Optional[Company]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Company], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Company:
        raise NotImplementedError

    @abstractmethod
    def update(self, company: Company, **attrs) -> Company:
        raise NotImplementedError


class DjangoCompanyRepository(CompanyRepository):
    def get_by_id(self, company_id: str) -> Optional[Company]:
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Company], int]:
        qs: QuerySet[Company] = Company.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(company_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Company:
        return Company.objects.create(**attrs)

    def update(self, company: Company, **attrs) -> Company:
        for k, v in attrs.items():
            setattr(company, k, v)
        company.save(update_fields=list(attrs.keys()))
        return company


class CompanyTypeRepository(ABC):
    @abstractmethod
    def get_by_id(self, company_type_id: str) -> Optional[CompanyType]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[CompanyType], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> CompanyType:
        raise NotImplementedError

    @abstractmethod
    def update(self, company_type: CompanyType, **attrs) -> CompanyType:
        raise NotImplementedError


class DjangoCompanyTypeRepository(CompanyTypeRepository):
    def get_by_id(self, company_type_id: str) -> Optional[CompanyType]:
        try:
            return CompanyType.objects.get(id=company_type_id)
        except CompanyType.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[CompanyType], int]:
        qs: QuerySet[CompanyType] = CompanyType.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(type_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> CompanyType:
        return CompanyType.objects.create(**attrs)

    def update(self, company_type: CompanyType, **attrs) -> CompanyType:
        for k, v in attrs.items():
            setattr(company_type, k, v)
        company_type.save(update_fields=list(attrs.keys()))
        return company_type


class CompanyBranchRepository(ABC):
    @abstractmethod
    def get_by_id(self, branch_id: str) -> Optional[CompanyBranch]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None) -> Tuple[Iterable[CompanyBranch], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> CompanyBranch:
        raise NotImplementedError

    @abstractmethod
    def update(self, branch: CompanyBranch, **attrs) -> CompanyBranch:
        raise NotImplementedError


class DjangoCompanyBranchRepository(CompanyBranchRepository):
    def get_by_id(self, branch_id: str) -> Optional[CompanyBranch]:
        try:
            return CompanyBranch.objects.select_related("company").get(id=branch_id)
        except CompanyBranch.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None) -> Tuple[Iterable[CompanyBranch], int]:
        qs: QuerySet[CompanyBranch] = CompanyBranch.objects.select_related("company").all().order_by("-created_date")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if search:
            qs = qs.filter(branch_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> CompanyBranch:
        return CompanyBranch.objects.create(**attrs)

    def update(self, branch: CompanyBranch, **attrs) -> CompanyBranch:
        for k, v in attrs.items():
            setattr(branch, k, v)
        branch.save(update_fields=list(attrs.keys()))
        return branch


class PlanRepository(ABC):
    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Plan], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Plan:
        raise NotImplementedError

    @abstractmethod
    def update(self, plan: Plan, **attrs) -> Plan:
        raise NotImplementedError


class DjangoPlanRepository(PlanRepository):
    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        try:
            return Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Plan], int]:
        qs: QuerySet[Plan] = Plan.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(plan_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Plan:
        return Plan.objects.create(**attrs)

    def update(self, plan: Plan, **attrs) -> Plan:
        for k, v in attrs.items():
            setattr(plan, k, v)
        plan.save(update_fields=list(attrs.keys()))
        return plan


class SchemePlanRepository(ABC):
    @abstractmethod
    def get_by_id(self, scheme_plan_id: str) -> Optional[SchemePlan]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None) -> Tuple[Iterable[SchemePlan], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> SchemePlan:
        raise NotImplementedError

    @abstractmethod
    def update(self, scheme_plan: SchemePlan, **attrs) -> SchemePlan:
        raise NotImplementedError


class DjangoSchemePlanRepository(SchemePlanRepository):
    def get_by_id(self, scheme_plan_id: str) -> Optional[SchemePlan]:
        try:
            return SchemePlan.objects.select_related("scheme", "plan").get(id=scheme_plan_id)
        except SchemePlan.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None) -> Tuple[Iterable[SchemePlan], int]:
        qs: QuerySet[SchemePlan] = SchemePlan.objects.select_related("scheme", "plan").all().order_by("-created_date")
        if scheme_id:
            qs = qs.filter(scheme_id=scheme_id)
        if search:
            qs = qs.filter(plan__plan_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> SchemePlan:
        return SchemePlan.objects.create(**attrs)

    def update(self, scheme_plan: SchemePlan, **attrs) -> SchemePlan:
        for k, v in attrs.items():
            setattr(scheme_plan, k, v)
        scheme_plan.save(update_fields=list(attrs.keys()))
        return scheme_plan


class BenefitRepository(ABC):
    @abstractmethod
    def get_by_id(self, benefit_id: str) -> Optional[Benefit]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Benefit], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Benefit:
        raise NotImplementedError

    @abstractmethod
    def update(self, benefit: Benefit, **attrs) -> Benefit:
        raise NotImplementedError


class DjangoBenefitRepository(BenefitRepository):
    def get_by_id(self, benefit_id: str) -> Optional[Benefit]:
        try:
            return Benefit.objects.get(id=benefit_id)
        except Benefit.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Benefit], int]:
        qs: QuerySet[Benefit] = Benefit.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(benefit_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Benefit:
        return Benefit.objects.create(**attrs)

    def update(self, benefit: Benefit, **attrs) -> Benefit:
        for k, v in attrs.items():
            setattr(benefit, k, v)
        benefit.save(update_fields=list(attrs.keys()))
        return benefit


class SchemeBenefitRepository(ABC):
    @abstractmethod
    def get_by_id(self, scheme_benefit_id: str) -> Optional[SchemeBenefit]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None) -> Tuple[Iterable[SchemeBenefit], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> SchemeBenefit:
        raise NotImplementedError

    @abstractmethod
    def update(self, scheme_benefit: SchemeBenefit, **attrs) -> SchemeBenefit:
        raise NotImplementedError


class DjangoSchemeBenefitRepository(SchemeBenefitRepository):
    def get_by_id(self, scheme_benefit_id: str) -> Optional[SchemeBenefit]:
        try:
            return SchemeBenefit.objects.select_related("scheme", "scheme_benefit").get(id=scheme_benefit_id)
        except SchemeBenefit.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None) -> Tuple[Iterable[SchemeBenefit], int]:
        qs: QuerySet[SchemeBenefit] = SchemeBenefit.objects.select_related("scheme", "scheme_benefit").all().order_by("-created_date")
        if scheme_id:
            qs = qs.filter(scheme_id=scheme_id)
        if search:
            qs = qs.filter(scheme_benefit__service_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> SchemeBenefit:
        return SchemeBenefit.objects.create(**attrs)

    def update(self, scheme_benefit: SchemeBenefit, **attrs) -> SchemeBenefit:
        for k, v in attrs.items():
            setattr(scheme_benefit, k, v)
        scheme_benefit.save(update_fields=list(attrs.keys()))
        return scheme_benefit


class MemberDependantRepository(ABC):
    @abstractmethod
    def get_by_id(self, dependant_id: str) -> Optional[MemberDependant]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None) -> Tuple[Iterable[MemberDependant], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> MemberDependant:
        raise NotImplementedError

    @abstractmethod
    def update(self, dependant: MemberDependant, **attrs) -> MemberDependant:
        raise NotImplementedError


class DjangoMemberDependantRepository(MemberDependantRepository):
    def get_by_id(self, dependant_id: str) -> Optional[MemberDependant]:
        try:
            return MemberDependant.objects.select_related("member").get(id=dependant_id)
        except MemberDependant.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None) -> Tuple[Iterable[MemberDependant], int]:
        qs: QuerySet[MemberDependant] = MemberDependant.objects.select_related("member").all().order_by("-created_date")
        if member_id:
            qs = qs.filter(member_id=member_id)
        if search:
            qs = qs.filter(dependant_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> MemberDependant:
        return MemberDependant.objects.create(**attrs)

    def update(self, dependant: MemberDependant, **attrs) -> MemberDependant:
        for k, v in attrs.items():
            setattr(dependant, k, v)
        dependant.save(update_fields=list(attrs.keys()))
        return dependant


class HospitalBranchRepository(ABC):
    @abstractmethod
    def get_by_id(self, branch_id: str) -> Optional[HospitalBranch]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalBranch], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> HospitalBranch:
        raise NotImplementedError

    @abstractmethod
    def update(self, branch: HospitalBranch, **attrs) -> HospitalBranch:
        raise NotImplementedError


class DjangoHospitalBranchRepository(HospitalBranchRepository):
    def get_by_id(self, branch_id: str) -> Optional[HospitalBranch]:
        try:
            return HospitalBranch.objects.select_related("hospital").get(id=branch_id)
        except HospitalBranch.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalBranch], int]:
        qs: QuerySet[HospitalBranch] = HospitalBranch.objects.select_related("hospital").all().order_by("-created_date")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if search:
            qs = qs.filter(branch_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> HospitalBranch:
        return HospitalBranch.objects.create(**attrs)

    def update(self, branch: HospitalBranch, **attrs) -> HospitalBranch:
        for k, v in attrs.items():
            setattr(branch, k, v)
        branch.save(update_fields=list(attrs.keys()))
        return branch


class HospitalDoctorRepository(ABC):
    @abstractmethod
    def get_by_id(self, doctor_id: str) -> Optional[HospitalDoctor]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalDoctor], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> HospitalDoctor:
        raise NotImplementedError

    @abstractmethod
    def update(self, doctor: HospitalDoctor, **attrs) -> HospitalDoctor:
        raise NotImplementedError


class DjangoHospitalDoctorRepository(HospitalDoctorRepository):
    def get_by_id(self, doctor_id: str) -> Optional[HospitalDoctor]:
        try:
            return HospitalDoctor.objects.select_related("hospital").get(id=doctor_id)
        except HospitalDoctor.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalDoctor], int]:
        qs: QuerySet[HospitalDoctor] = HospitalDoctor.objects.select_related("hospital").all().order_by("-created_date")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if search:
            qs = qs.filter(doctor_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> HospitalDoctor:
        return HospitalDoctor.objects.create(**attrs)

    def update(self, doctor: HospitalDoctor, **attrs) -> HospitalDoctor:
        for k, v in attrs.items():
            setattr(doctor, k, v)
        doctor.save(update_fields=list(attrs.keys()))
        return doctor


class HospitalMedicineRepository(ABC):
    @abstractmethod
    def get_by_id(self, hospital_medicine_id: str) -> Optional[HospitalMedicine]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalMedicine], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> HospitalMedicine:
        raise NotImplementedError

    @abstractmethod
    def update(self, hospital_medicine: HospitalMedicine, **attrs) -> HospitalMedicine:
        raise NotImplementedError


class DjangoHospitalMedicineRepository(HospitalMedicineRepository):
    def get_by_id(self, hospital_medicine_id: str) -> Optional[HospitalMedicine]:
        try:
            return HospitalMedicine.objects.select_related("hospital", "medicine").get(id=hospital_medicine_id)
        except HospitalMedicine.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalMedicine], int]:
        qs: QuerySet[HospitalMedicine] = HospitalMedicine.objects.select_related("hospital", "medicine").all().order_by("-created_date")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if search:
            qs = qs.filter(medicine__medicine_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> HospitalMedicine:
        return HospitalMedicine.objects.create(**attrs)

    def update(self, hospital_medicine: HospitalMedicine, **attrs) -> HospitalMedicine:
        for k, v in attrs.items():
            setattr(hospital_medicine, k, v)
        hospital_medicine.save(update_fields=list(attrs.keys()))
        return hospital_medicine


class HospitalServiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, hospital_service_id: str) -> Optional[HospitalService]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalService], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> HospitalService:
        raise NotImplementedError

    @abstractmethod
    def update(self, hospital_service: HospitalService, **attrs) -> HospitalService:
        raise NotImplementedError


class DjangoHospitalServiceRepository(HospitalServiceRepository):
    def get_by_id(self, hospital_service_id: str) -> Optional[HospitalService]:
        try:
            return HospitalService.objects.select_related("hospital", "service").get(id=hospital_service_id)
        except HospitalService.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalService], int]:
        qs: QuerySet[HospitalService] = HospitalService.objects.select_related("hospital", "service").all().order_by("-created_date")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if search:
            qs = qs.filter(service__service_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> HospitalService:
        return HospitalService.objects.create(**attrs)

    def update(self, hospital_service: HospitalService, **attrs) -> HospitalService:
        for k, v in attrs.items():
            setattr(hospital_service, k, v)
        hospital_service.save(update_fields=list(attrs.keys()))
        return hospital_service


class HospitalLabTestRepository(ABC):
    @abstractmethod
    def get_by_id(self, hospital_lab_test_id: str) -> Optional[HospitalLabTest]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalLabTest], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> HospitalLabTest:
        raise NotImplementedError

    @abstractmethod
    def update(self, hospital_lab_test: HospitalLabTest, **attrs) -> HospitalLabTest:
        raise NotImplementedError


class DjangoHospitalLabTestRepository(HospitalLabTestRepository):
    def get_by_id(self, hospital_lab_test_id: str) -> Optional[HospitalLabTest]:
        try:
            return HospitalLabTest.objects.select_related("hospital", "labtest").get(id=hospital_lab_test_id)
        except HospitalLabTest.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None) -> Tuple[Iterable[HospitalLabTest], int]:
        qs: QuerySet[HospitalLabTest] = HospitalLabTest.objects.select_related("hospital", "labtest").all().order_by("-created_date")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if search:
            qs = qs.filter(labtest__test_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> HospitalLabTest:
        return HospitalLabTest.objects.create(**attrs)

    def update(self, hospital_lab_test: HospitalLabTest, **attrs) -> HospitalLabTest:
        for k, v in attrs.items():
            setattr(hospital_lab_test, k, v)
        hospital_lab_test.save(update_fields=list(attrs.keys()))
        return hospital_lab_test


class MedicineRepository(ABC):
    @abstractmethod
    def get_by_id(self, medicine_id: str) -> Optional[Medicine]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Medicine], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Medicine:
        raise NotImplementedError

    @abstractmethod
    def update(self, medicine: Medicine, **attrs) -> Medicine:
        raise NotImplementedError


class DjangoMedicineRepository(MedicineRepository):
    def get_by_id(self, medicine_id: str) -> Optional[Medicine]:
        try:
            return Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Medicine], int]:
        qs: QuerySet[Medicine] = Medicine.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(medicine_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Medicine:
        return Medicine.objects.create(**attrs)

    def update(self, medicine: Medicine, **attrs) -> Medicine:
        for k, v in attrs.items():
            setattr(medicine, k, v)
        medicine.save(update_fields=list(attrs.keys()))
        return medicine


class ServiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, service_id: str) -> Optional[Service]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Service], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Service:
        raise NotImplementedError

    @abstractmethod
    def update(self, service: Service, **attrs) -> Service:
        raise NotImplementedError


class DjangoServiceRepository(ServiceRepository):
    def get_by_id(self, service_id: str) -> Optional[Service]:
        try:
            return Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Service], int]:
        qs: QuerySet[Service] = Service.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(service_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Service:
        return Service.objects.create(**attrs)

    def update(self, service: Service, **attrs) -> Service:
        for k, v in attrs.items():
            setattr(service, k, v)
        service.save(update_fields=list(attrs.keys()))
        return service


class LabTestRepository(ABC):
    @abstractmethod
    def get_by_id(self, lab_test_id: str) -> Optional[LabTest]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[LabTest], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> LabTest:
        raise NotImplementedError

    @abstractmethod
    def update(self, lab_test: LabTest, **attrs) -> LabTest:
        raise NotImplementedError


class DjangoLabTestRepository(LabTestRepository):
    def get_by_id(self, lab_test_id: str) -> Optional[LabTest]:
        try:
            return LabTest.objects.get(id=lab_test_id)
        except LabTest.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[LabTest], int]:
        qs: QuerySet[LabTest] = LabTest.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(test_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> LabTest:
        return LabTest.objects.create(**attrs)

    def update(self, lab_test: LabTest, **attrs) -> LabTest:
        for k, v in attrs.items():
            setattr(lab_test, k, v)
        lab_test.save(update_fields=list(attrs.keys()))
        return lab_test


class DiagnosisRepository(ABC):
    @abstractmethod
    def get_by_id(self, diagnosis_id: str) -> Optional[Diagnosis]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Diagnosis], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Diagnosis:
        raise NotImplementedError

    @abstractmethod
    def update(self, diagnosis: Diagnosis, **attrs) -> Diagnosis:
        raise NotImplementedError


class DjangoDiagnosisRepository(DiagnosisRepository):
    def get_by_id(self, diagnosis_id: str) -> Optional[Diagnosis]:
        try:
            return Diagnosis.objects.get(id=diagnosis_id)
        except Diagnosis.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Diagnosis], int]:
        qs: QuerySet[Diagnosis] = Diagnosis.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(diagnosis_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Diagnosis:
        return Diagnosis.objects.create(**attrs)

    def update(self, diagnosis: Diagnosis, **attrs) -> Diagnosis:
        for k, v in attrs.items():
            setattr(diagnosis, k, v)
        diagnosis.save(update_fields=list(attrs.keys()))
        return diagnosis


class ClaimRepository(ABC):
    @abstractmethod
    def get_by_id(self, claim_id: str) -> Optional[Claim]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None) -> Tuple[Iterable[Claim], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> Claim:
        raise NotImplementedError

    @abstractmethod
    def update(self, claim: Claim, **attrs) -> Claim:
        raise NotImplementedError


class DjangoClaimRepository(ClaimRepository):
    def get_by_id(self, claim_id: str) -> Optional[Claim]:
        try:
            return Claim.objects.select_related("member", "hospital").get(id=claim_id)
        except Claim.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None) -> Tuple[Iterable[Claim], int]:
        qs: QuerySet[Claim] = Claim.objects.select_related("member", "hospital").all().order_by("-created_date")
        if member_id:
            qs = qs.filter(member_id=member_id)
        if search:
            qs = qs.filter(claim_number__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> Claim:
        return Claim.objects.create(**attrs)

    def update(self, claim: Claim, **attrs) -> Claim:
        for k, v in attrs.items():
            setattr(claim, k, v)
        claim.save(update_fields=list(attrs.keys()))
        return claim


class ClaimDetailRepository(ABC):
    @abstractmethod
    def get_by_id(self, claim_detail_id: str) -> Optional[ClaimDetail]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None) -> Tuple[Iterable[ClaimDetail], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> ClaimDetail:
        raise NotImplementedError

    @abstractmethod
    def update(self, claim_detail: ClaimDetail, **attrs) -> ClaimDetail:
        raise NotImplementedError


class DjangoClaimDetailRepository(ClaimDetailRepository):
    def get_by_id(self, claim_detail_id: str) -> Optional[ClaimDetail]:
        try:
            return ClaimDetail.objects.select_related("claim").get(id=claim_detail_id)
        except ClaimDetail.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None) -> Tuple[Iterable[ClaimDetail], int]:
        qs: QuerySet[ClaimDetail] = ClaimDetail.objects.select_related("claim").all().order_by("-created_date")
        if claim_id:
            qs = qs.filter(claim_id=claim_id)
        if search:
            qs = qs.filter(description__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> ClaimDetail:
        return ClaimDetail.objects.create(**attrs)

    def update(self, claim_detail: ClaimDetail, **attrs) -> ClaimDetail:
        for k, v in attrs.items():
            setattr(claim_detail, k, v)
        claim_detail.save(update_fields=list(attrs.keys()))
        return claim_detail


class ClaimPaymentRepository(ABC):
    @abstractmethod
    def get_by_id(self, claim_payment_id: str) -> Optional[ClaimPayment]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None) -> Tuple[Iterable[ClaimPayment], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> ClaimPayment:
        raise NotImplementedError

    @abstractmethod
    def update(self, claim_payment: ClaimPayment, **attrs) -> ClaimPayment:
        raise NotImplementedError


class DjangoClaimPaymentRepository(ClaimPaymentRepository):
    def get_by_id(self, claim_payment_id: str) -> Optional[ClaimPayment]:
        try:
            return ClaimPayment.objects.select_related("claim").get(id=claim_payment_id)
        except ClaimPayment.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None) -> Tuple[Iterable[ClaimPayment], int]:
        qs: QuerySet[ClaimPayment] = ClaimPayment.objects.select_related("claim").all().order_by("-created_date")
        if claim_id:
            qs = qs.filter(claim_id=claim_id)
        if search:
            qs = qs.filter(payment_reference__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> ClaimPayment:
        return ClaimPayment.objects.create(**attrs)

    def update(self, claim_payment: ClaimPayment, **attrs) -> ClaimPayment:
        for k, v in attrs.items():
            setattr(claim_payment, k, v)
        claim_payment.save(update_fields=list(attrs.keys()))
        return claim_payment


class BillingSessionRepository(ABC):
    @abstractmethod
    def get_by_id(self, billing_session_id: str) -> Optional[BillingSession]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[BillingSession], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> BillingSession:
        raise NotImplementedError

    @abstractmethod
    def update(self, billing_session: BillingSession, **attrs) -> BillingSession:
        raise NotImplementedError


class DjangoBillingSessionRepository(BillingSessionRepository):
    def get_by_id(self, billing_session_id: str) -> Optional[BillingSession]:
        try:
            return BillingSession.objects.get(id=billing_session_id)
        except BillingSession.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[BillingSession], int]:
        qs: QuerySet[BillingSession] = BillingSession.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(session_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> BillingSession:
        return BillingSession.objects.create(**attrs)

    def update(self, billing_session: BillingSession, **attrs) -> BillingSession:
        for k, v in attrs.items():
            setattr(billing_session, k, v)
        billing_session.save(update_fields=list(attrs.keys()))
        return billing_session


class DistrictRepository(ABC):
    @abstractmethod
    def get_by_id(self, district_id: str) -> Optional[District]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[District], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> District:
        raise NotImplementedError

    @abstractmethod
    def update(self, district: District, **attrs) -> District:
        raise NotImplementedError


class DjangoDistrictRepository(DistrictRepository):
    def get_by_id(self, district_id: str) -> Optional[District]:
        try:
            return District.objects.get(id=district_id)
        except District.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[District], int]:
        qs: QuerySet[District] = District.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(district_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> District:
        return District.objects.create(**attrs)

    def update(self, district: District, **attrs) -> District:
        for k, v in attrs.items():
            setattr(district, k, v)
        district.save(update_fields=list(attrs.keys()))
        return district


class FinancialPeriodRepository(ABC):
    @abstractmethod
    def get_by_id(self, financial_period_id: str) -> Optional[FinancialPeriod]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[FinancialPeriod], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> FinancialPeriod:
        raise NotImplementedError

    @abstractmethod
    def update(self, financial_period: FinancialPeriod, **attrs) -> FinancialPeriod:
        raise NotImplementedError


class DjangoFinancialPeriodRepository(FinancialPeriodRepository):
    def get_by_id(self, financial_period_id: str) -> Optional[FinancialPeriod]:
        try:
            return FinancialPeriod.objects.get(id=financial_period_id)
        except FinancialPeriod.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[FinancialPeriod], int]:
        qs: QuerySet[FinancialPeriod] = FinancialPeriod.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(period_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> FinancialPeriod:
        return FinancialPeriod.objects.create(**attrs)

    def update(self, financial_period: FinancialPeriod, **attrs) -> FinancialPeriod:
        for k, v in attrs.items():
            setattr(financial_period, k, v)
        financial_period.save(update_fields=list(attrs.keys()))
        return financial_period


class ApplicationUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[ApplicationUser]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[ApplicationUser], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> ApplicationUser:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: ApplicationUser, **attrs) -> ApplicationUser:
        raise NotImplementedError


class DjangoApplicationUserRepository(ApplicationUserRepository):
    def get_by_id(self, user_id: str) -> Optional[ApplicationUser]:
        try:
            return ApplicationUser.objects.get(id=user_id)
        except ApplicationUser.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[ApplicationUser], int]:
        qs: QuerySet[ApplicationUser] = ApplicationUser.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(username__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> ApplicationUser:
        return ApplicationUser.objects.create(**attrs)

    def update(self, user: ApplicationUser, **attrs) -> ApplicationUser:
        for k, v in attrs.items():
            setattr(user, k, v)
        user.save(update_fields=list(attrs.keys()))
        return user


class ApplicationModuleRepository(ABC):
    @abstractmethod
    def get_by_id(self, module_id: str) -> Optional[ApplicationModule]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[ApplicationModule], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> ApplicationModule:
        raise NotImplementedError

    @abstractmethod
    def update(self, module: ApplicationModule, **attrs) -> ApplicationModule:
        raise NotImplementedError


class DjangoApplicationModuleRepository(ApplicationModuleRepository):
    def get_by_id(self, module_id: str) -> Optional[ApplicationModule]:
        try:
            return ApplicationModule.objects.get(id=module_id)
        except ApplicationModule.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[ApplicationModule], int]:
        qs: QuerySet[ApplicationModule] = ApplicationModule.objects.all().order_by("-created_date")
        if search:
            qs = qs.filter(module_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> ApplicationModule:
        return ApplicationModule.objects.create(**attrs)

    def update(self, module: ApplicationModule, **attrs) -> ApplicationModule:
        for k, v in attrs.items():
            setattr(module, k, v)
        module.save(update_fields=list(attrs.keys()))
        return module


class UserPermissionRepository(ABC):
    @abstractmethod
    def get_by_id(self, permission_id: str) -> Optional[UserPermission]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, user_id: Optional[str] = None) -> Tuple[Iterable[UserPermission], int]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **attrs) -> UserPermission:
        raise NotImplementedError

    @abstractmethod
    def update(self, permission: UserPermission, **attrs) -> UserPermission:
        raise NotImplementedError


class DjangoUserPermissionRepository(UserPermissionRepository):
    def get_by_id(self, permission_id: str) -> Optional[UserPermission]:
        try:
            return UserPermission.objects.select_related("user", "module").get(id=permission_id)
        except UserPermission.DoesNotExist:
            return None

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, user_id: Optional[str] = None) -> Tuple[Iterable[UserPermission], int]:
        qs: QuerySet[UserPermission] = UserPermission.objects.select_related("user", "module").all().order_by("-created_date")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if search:
            qs = qs.filter(permission_name__icontains=search)
        total = qs.count()
        return qs[offset: offset + limit], total

    def create(self, **attrs) -> UserPermission:
        return UserPermission.objects.create(**attrs)

    def update(self, permission: UserPermission, **attrs) -> UserPermission:
        for k, v in attrs.items():
            setattr(permission, k, v)
        permission.save(update_fields=list(attrs.keys()))
        return permission


