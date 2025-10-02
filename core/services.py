from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable, Tuple

from django.db import transaction

from .models import Member, StatusChoices, Scheme, Hospital, Company, CompanyType, CompanyBranch, Plan, SchemePlan, Benefit, SchemeBenefit, MemberDependant, HospitalBranch, HospitalDoctor, HospitalMedicine, HospitalService, HospitalLabTest, Medicine, Service, LabTest, Diagnosis, Claim, ClaimDetail, ClaimPayment, BillingSession, District, FinancialPeriod, ApplicationUser, ApplicationModule, UserPermission
from .repositories import MemberRepository, SchemeRepository, HospitalRepository, CompanyRepository, CompanyTypeRepository, CompanyBranchRepository, PlanRepository, SchemePlanRepository, BenefitRepository, SchemeBenefitRepository, MemberDependantRepository, HospitalBranchRepository, HospitalDoctorRepository, HospitalMedicineRepository, HospitalServiceRepository, HospitalLabTestRepository, MedicineRepository, ServiceRepository, LabTestRepository, DiagnosisRepository, ClaimRepository, ClaimDetailRepository, ClaimPaymentRepository, BillingSessionRepository, DistrictRepository, FinancialPeriodRepository, ApplicationUserRepository, ApplicationModuleRepository, UserPermissionRepository


@dataclass
class MemberCreateDTO:
    member_name: str
    company_id: str
    scheme_id: str
    employee_id: str = ""
    national_id: str = ""
    gender: str = ""
    phone_mobile: str = ""
    email: str = ""
    card_number: str = ""


@dataclass
class MemberUpdateDTO:
    member_name: Optional[str] = None
    employee_id: Optional[str] = None
    national_id: Optional[str] = None
    gender: Optional[str] = None
    phone_mobile: Optional[str] = None
    email: Optional[str] = None


class MemberService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo

    def list_members(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[Iterable[Member], int]:
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create_member(self, data: MemberCreateDTO) -> Member:
        # Basic business rules example: enforce unique card_number if provided
        if not data.member_name or not data.company_id or not data.scheme_id:
            raise ValueError("member_name, company_id and scheme_id are required")
        attrs = {
            "member_name": data.member_name,
            "company_id": data.company_id,
            "scheme_id": data.scheme_id,
            "employee_id": data.employee_id,
            "national_id": data.national_id,
            "gender": data.gender,
            "phone_mobile": data.phone_mobile,
            "email": data.email,
            "card_number": data.card_number,
        }
        if data.card_number:
            if Member.objects.filter(card_number=data.card_number).exists():
                raise ValueError("Card number already in use")
        member = self.repo.create(**attrs)
        return member

    @transaction.atomic
    def update_member(self, member_id: str, data: MemberUpdateDTO) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise ValueError("Member not found")
        updates = {k: v for k, v in data.__dict__.items() if v is not None}
        return self.repo.update(member, **updates)

    @transaction.atomic
    def activate_member(self, member_id: str) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise ValueError("Member not found")
        return self.repo.update(member, member_status=StatusChoices.ACTIVE)

    @transaction.atomic
    def deactivate_member(self, member_id: str) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise ValueError("Member not found")
        return self.repo.update(member, member_status=StatusChoices.INACTIVE)


class SchemeService:
    def __init__(self, repo: SchemeRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, company_id=company_id)

    @transaction.atomic
    def create(self, *, scheme_name: str, company_id: str, beginningdate: str, endingdate: str, **attrs) -> Scheme:
        if not scheme_name or not company_id or not beginningdate or not endingdate:
            raise ValueError("scheme_name, company_id, beginningdate, endingdate are required")
        return self.repo.create(scheme_name=scheme_name, company_id=company_id, beginningdate=beginningdate, endingdate=endingdate, **attrs)

    @transaction.atomic
    def update(self, scheme_id: str, **attrs) -> Scheme:
        scheme = self.repo.get_by_id(scheme_id)
        if not scheme:
            raise ValueError("Scheme not found")
        return self.repo.update(scheme, **attrs)


class HospitalService:
    def __init__(self, repo: HospitalRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, hospital_reference: str, hospital_name: str, **attrs) -> Hospital:
        if not hospital_reference or not hospital_name:
            raise ValueError("hospital_reference and hospital_name are required")
        if Hospital.objects.filter(hospital_reference=hospital_reference).exists():
            raise ValueError("hospital_reference already exists")
        return self.repo.create(hospital_reference=hospital_reference, hospital_name=hospital_name, **attrs)

    @transaction.atomic
    def update(self, hospital_id: str, **attrs) -> Hospital:
        hospital = self.repo.get_by_id(hospital_id)
        if not hospital:
            raise ValueError("Hospital not found")
        return self.repo.update(hospital, **attrs)


class CompanyService:
    def __init__(self, repo: CompanyRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, company_name: str, **attrs) -> Company:
        if not company_name:
            raise ValueError("company_name is required")
        if Company.objects.filter(company_name=company_name).exists():
            raise ValueError("company_name already exists")
        return self.repo.create(company_name=company_name, **attrs)

    @transaction.atomic
    def update(self, company_id: str, **attrs) -> Company:
        company = self.repo.get_by_id(company_id)
        if not company:
            raise ValueError("Company not found")
        return self.repo.update(company, **attrs)


class CompanyTypeService:
    def __init__(self, repo: CompanyTypeRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, type_name: str, **attrs) -> CompanyType:
        if not type_name:
            raise ValueError("type_name is required")
        if CompanyType.objects.filter(type_name=type_name).exists():
            raise ValueError("type_name already exists")
        return self.repo.create(type_name=type_name, **attrs)

    @transaction.atomic
    def update(self, company_type_id: str, **attrs) -> CompanyType:
        company_type = self.repo.get_by_id(company_type_id)
        if not company_type:
            raise ValueError("CompanyType not found")
        return self.repo.update(company_type, **attrs)


class CompanyBranchService:
    def __init__(self, repo: CompanyBranchRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, company_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, company_id=company_id)

    @transaction.atomic
    def create(self, *, branch_name: str, company_id: str, **attrs) -> CompanyBranch:
        if not branch_name or not company_id:
            raise ValueError("branch_name and company_id are required")
        return self.repo.create(branch_name=branch_name, company_id=company_id, **attrs)

    @transaction.atomic
    def update(self, branch_id: str, **attrs) -> CompanyBranch:
        branch = self.repo.get_by_id(branch_id)
        if not branch:
            raise ValueError("CompanyBranch not found")
        return self.repo.update(branch, **attrs)


class PlanService:
    def __init__(self, repo: PlanRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, plan_name: str, **attrs) -> Plan:
        if not plan_name:
            raise ValueError("plan_name is required")
        if Plan.objects.filter(plan_name=plan_name).exists():
            raise ValueError("plan_name already exists")
        return self.repo.create(plan_name=plan_name, **attrs)

    @transaction.atomic
    def update(self, plan_id: str, **attrs) -> Plan:
        plan = self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        return self.repo.update(plan, **attrs)


class SchemePlanService:
    def __init__(self, repo: SchemePlanRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, scheme_id=scheme_id)

    @transaction.atomic
    def create(self, *, scheme_id: str, plan_id: str, **attrs) -> SchemePlan:
        if not scheme_id or not plan_id:
            raise ValueError("scheme_id and plan_id are required")
        return self.repo.create(scheme_id=scheme_id, plan_id=plan_id, **attrs)

    @transaction.atomic
    def update(self, scheme_plan_id: str, **attrs) -> SchemePlan:
        scheme_plan = self.repo.get_by_id(scheme_plan_id)
        if not scheme_plan:
            raise ValueError("SchemePlan not found")
        return self.repo.update(scheme_plan, **attrs)


class BenefitService:
    def __init__(self, repo: BenefitRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, benefit_name: str, **attrs) -> Benefit:
        if not benefit_name:
            raise ValueError("benefit_name is required")
        if Benefit.objects.filter(benefit_name=benefit_name).exists():
            raise ValueError("benefit_name already exists")
        return self.repo.create(benefit_name=benefit_name, **attrs)

    @transaction.atomic
    def update(self, benefit_id: str, **attrs) -> Benefit:
        benefit = self.repo.get_by_id(benefit_id)
        if not benefit:
            raise ValueError("Benefit not found")
        return self.repo.update(benefit, **attrs)


class SchemeBenefitService:
    def __init__(self, repo: SchemeBenefitRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, scheme_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, scheme_id=scheme_id)

    @transaction.atomic
    def create(self, *, scheme_id: str, benefit_id: str, **attrs) -> SchemeBenefit:
        if not scheme_id or not benefit_id:
            raise ValueError("scheme_id and benefit_id are required")
        return self.repo.create(scheme_id=scheme_id, benefit_id=benefit_id, **attrs)

    @transaction.atomic
    def update(self, scheme_benefit_id: str, **attrs) -> SchemeBenefit:
        scheme_benefit = self.repo.get_by_id(scheme_benefit_id)
        if not scheme_benefit:
            raise ValueError("SchemeBenefit not found")
        return self.repo.update(scheme_benefit, **attrs)


class MemberDependantService:
    def __init__(self, repo: MemberDependantRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, member_id=member_id)

    @transaction.atomic
    def create(self, *, member_id: str, dependant_name: str, **attrs) -> MemberDependant:
        if not member_id or not dependant_name:
            raise ValueError("member_id and dependant_name are required")
        return self.repo.create(member_id=member_id, dependant_name=dependant_name, **attrs)

    @transaction.atomic
    def update(self, dependant_id: str, **attrs) -> MemberDependant:
        dependant = self.repo.get_by_id(dependant_id)
        if not dependant:
            raise ValueError("MemberDependant not found")
        return self.repo.update(dependant, **attrs)


class HospitalBranchService:
    def __init__(self, repo: HospitalBranchRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, hospital_id=hospital_id)

    @transaction.atomic
    def create(self, *, hospital_id: str, branch_name: str, **attrs) -> HospitalBranch:
        if not hospital_id or not branch_name:
            raise ValueError("hospital_id and branch_name are required")
        return self.repo.create(hospital_id=hospital_id, branch_name=branch_name, **attrs)

    @transaction.atomic
    def update(self, branch_id: str, **attrs) -> HospitalBranch:
        branch = self.repo.get_by_id(branch_id)
        if not branch:
            raise ValueError("HospitalBranch not found")
        return self.repo.update(branch, **attrs)


class HospitalDoctorService:
    def __init__(self, repo: HospitalDoctorRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, hospital_id=hospital_id)

    @transaction.atomic
    def create(self, *, hospital_id: str, doctor_name: str, **attrs) -> HospitalDoctor:
        if not hospital_id or not doctor_name:
            raise ValueError("hospital_id and doctor_name are required")
        return self.repo.create(hospital_id=hospital_id, doctor_name=doctor_name, **attrs)

    @transaction.atomic
    def update(self, doctor_id: str, **attrs) -> HospitalDoctor:
        doctor = self.repo.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("HospitalDoctor not found")
        return self.repo.update(doctor, **attrs)


class HospitalMedicineService:
    def __init__(self, repo: HospitalMedicineRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, hospital_id=hospital_id)

    @transaction.atomic
    def create(self, *, hospital_id: str, medicine_id: str, **attrs) -> HospitalMedicine:
        if not hospital_id or not medicine_id:
            raise ValueError("hospital_id and medicine_id are required")
        return self.repo.create(hospital_id=hospital_id, medicine_id=medicine_id, **attrs)

    @transaction.atomic
    def update(self, hospital_medicine_id: str, **attrs) -> HospitalMedicine:
        hospital_medicine = self.repo.get_by_id(hospital_medicine_id)
        if not hospital_medicine:
            raise ValueError("HospitalMedicine not found")
        return self.repo.update(hospital_medicine, **attrs)


class HospitalServiceService:
    def __init__(self, repo: HospitalServiceRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, hospital_id=hospital_id)

    @transaction.atomic
    def create(self, *, hospital_id: str, service_id: str, **attrs) -> HospitalService:
        if not hospital_id or not service_id:
            raise ValueError("hospital_id and service_id are required")
        return self.repo.create(hospital_id=hospital_id, service_id=service_id, **attrs)

    @transaction.atomic
    def update(self, hospital_service_id: str, **attrs) -> HospitalService:
        hospital_service = self.repo.get_by_id(hospital_service_id)
        if not hospital_service:
            raise ValueError("HospitalService not found")
        return self.repo.update(hospital_service, **attrs)


class HospitalLabTestService:
    def __init__(self, repo: HospitalLabTestRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, hospital_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, hospital_id=hospital_id)

    @transaction.atomic
    def create(self, *, hospital_id: str, lab_test_id: str, **attrs) -> HospitalLabTest:
        if not hospital_id or not lab_test_id:
            raise ValueError("hospital_id and lab_test_id are required")
        return self.repo.create(hospital_id=hospital_id, lab_test_id=lab_test_id, **attrs)

    @transaction.atomic
    def update(self, hospital_lab_test_id: str, **attrs) -> HospitalLabTest:
        hospital_lab_test = self.repo.get_by_id(hospital_lab_test_id)
        if not hospital_lab_test:
            raise ValueError("HospitalLabTest not found")
        return self.repo.update(hospital_lab_test, **attrs)


class MedicineService:
    def __init__(self, repo: MedicineRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, medicine_name: str, **attrs) -> Medicine:
        if not medicine_name:
            raise ValueError("medicine_name is required")
        if Medicine.objects.filter(medicine_name=medicine_name).exists():
            raise ValueError("medicine_name already exists")
        return self.repo.create(medicine_name=medicine_name, **attrs)

    @transaction.atomic
    def update(self, medicine_id: str, **attrs) -> Medicine:
        medicine = self.repo.get_by_id(medicine_id)
        if not medicine:
            raise ValueError("Medicine not found")
        return self.repo.update(medicine, **attrs)


class ServiceService:
    def __init__(self, repo: ServiceRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, service_name: str, **attrs) -> Service:
        if not service_name:
            raise ValueError("service_name is required")
        if Service.objects.filter(service_name=service_name).exists():
            raise ValueError("service_name already exists")
        return self.repo.create(service_name=service_name, **attrs)

    @transaction.atomic
    def update(self, service_id: str, **attrs) -> Service:
        service = self.repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        return self.repo.update(service, **attrs)


class LabTestService:
    def __init__(self, repo: LabTestRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, test_name: str, **attrs) -> LabTest:
        if not test_name:
            raise ValueError("test_name is required")
        if LabTest.objects.filter(test_name=test_name).exists():
            raise ValueError("test_name already exists")
        return self.repo.create(test_name=test_name, **attrs)

    @transaction.atomic
    def update(self, lab_test_id: str, **attrs) -> LabTest:
        lab_test = self.repo.get_by_id(lab_test_id)
        if not lab_test:
            raise ValueError("LabTest not found")
        return self.repo.update(lab_test, **attrs)


class DiagnosisService:
    def __init__(self, repo: DiagnosisRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, diagnosis_name: str, **attrs) -> Diagnosis:
        if not diagnosis_name:
            raise ValueError("diagnosis_name is required")
        if Diagnosis.objects.filter(diagnosis_name=diagnosis_name).exists():
            raise ValueError("diagnosis_name already exists")
        return self.repo.create(diagnosis_name=diagnosis_name, **attrs)

    @transaction.atomic
    def update(self, diagnosis_id: str, **attrs) -> Diagnosis:
        diagnosis = self.repo.get_by_id(diagnosis_id)
        if not diagnosis:
            raise ValueError("Diagnosis not found")
        return self.repo.update(diagnosis, **attrs)


class ClaimService:
    def __init__(self, repo: ClaimRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, member_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, member_id=member_id)

    @transaction.atomic
    def create(self, *, member_id: str, hospital_id: str, claim_number: str, **attrs) -> Claim:
        if not member_id or not hospital_id or not claim_number:
            raise ValueError("member_id, hospital_id, and claim_number are required")
        if Claim.objects.filter(claim_number=claim_number).exists():
            raise ValueError("claim_number already exists")
        return self.repo.create(member_id=member_id, hospital_id=hospital_id, claim_number=claim_number, **attrs)

    @transaction.atomic
    def update(self, claim_id: str, **attrs) -> Claim:
        claim = self.repo.get_by_id(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        return self.repo.update(claim, **attrs)


class ClaimDetailService:
    def __init__(self, repo: ClaimDetailRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, claim_id=claim_id)

    @transaction.atomic
    def create(self, *, claim_id: str, description: str, **attrs) -> ClaimDetail:
        if not claim_id or not description:
            raise ValueError("claim_id and description are required")
        return self.repo.create(claim_id=claim_id, description=description, **attrs)

    @transaction.atomic
    def update(self, claim_detail_id: str, **attrs) -> ClaimDetail:
        claim_detail = self.repo.get_by_id(claim_detail_id)
        if not claim_detail:
            raise ValueError("ClaimDetail not found")
        return self.repo.update(claim_detail, **attrs)


class ClaimPaymentService:
    def __init__(self, repo: ClaimPaymentRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, claim_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, claim_id=claim_id)

    @transaction.atomic
    def create(self, *, claim_id: str, payment_reference: str, amount: float, **attrs) -> ClaimPayment:
        if not claim_id or not payment_reference or amount is None:
            raise ValueError("claim_id, payment_reference, and amount are required")
        return self.repo.create(claim_id=claim_id, payment_reference=payment_reference, amount=amount, **attrs)

    @transaction.atomic
    def update(self, claim_payment_id: str, **attrs) -> ClaimPayment:
        claim_payment = self.repo.get_by_id(claim_payment_id)
        if not claim_payment:
            raise ValueError("ClaimPayment not found")
        return self.repo.update(claim_payment, **attrs)


class BillingSessionService:
    def __init__(self, repo: BillingSessionRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, session_name: str, **attrs) -> BillingSession:
        if not session_name:
            raise ValueError("session_name is required")
        if BillingSession.objects.filter(session_name=session_name).exists():
            raise ValueError("session_name already exists")
        return self.repo.create(session_name=session_name, **attrs)

    @transaction.atomic
    def update(self, billing_session_id: str, **attrs) -> BillingSession:
        billing_session = self.repo.get_by_id(billing_session_id)
        if not billing_session:
            raise ValueError("BillingSession not found")
        return self.repo.update(billing_session, **attrs)


class DistrictService:
    def __init__(self, repo: DistrictRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, district_name: str, **attrs) -> District:
        if not district_name:
            raise ValueError("district_name is required")
        if District.objects.filter(district_name=district_name).exists():
            raise ValueError("district_name already exists")
        return self.repo.create(district_name=district_name, **attrs)

    @transaction.atomic
    def update(self, district_id: str, **attrs) -> District:
        district = self.repo.get_by_id(district_id)
        if not district:
            raise ValueError("District not found")
        return self.repo.update(district, **attrs)


class FinancialPeriodService:
    def __init__(self, repo: FinancialPeriodRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, period_name: str, start_date, end_date, **attrs) -> FinancialPeriod:
        if not period_name or not start_date or not end_date:
            raise ValueError("period_name, start_date, and end_date are required")
        if FinancialPeriod.objects.filter(period_name=period_name).exists():
            raise ValueError("period_name already exists")
        return self.repo.create(period_name=period_name, start_date=start_date, end_date=end_date, **attrs)

    @transaction.atomic
    def update(self, financial_period_id: str, **attrs) -> FinancialPeriod:
        financial_period = self.repo.get_by_id(financial_period_id)
        if not financial_period:
            raise ValueError("FinancialPeriod not found")
        return self.repo.update(financial_period, **attrs)


class ApplicationUserService:
    def __init__(self, repo: ApplicationUserRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, username: str, **attrs) -> ApplicationUser:
        if not username:
            raise ValueError("username is required")
        if ApplicationUser.objects.filter(username=username).exists():
            raise ValueError("username already exists")
        return self.repo.create(username=username, **attrs)

    @transaction.atomic
    def update(self, user_id: str, **attrs) -> ApplicationUser:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("ApplicationUser not found")
        return self.repo.update(user, **attrs)


class ApplicationModuleService:
    def __init__(self, repo: ApplicationModuleRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repo.list(search=search, limit=limit, offset=offset)

    @transaction.atomic
    def create(self, *, module_name: str, **attrs) -> ApplicationModule:
        if not module_name:
            raise ValueError("module_name is required")
        if ApplicationModule.objects.filter(module_name=module_name).exists():
            raise ValueError("module_name already exists")
        return self.repo.create(module_name=module_name, **attrs)

    @transaction.atomic
    def update(self, module_id: str, **attrs) -> ApplicationModule:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ValueError("ApplicationModule not found")
        return self.repo.update(module, **attrs)


class UserPermissionService:
    def __init__(self, repo: UserPermissionRepository):
        self.repo = repo

    def list(self, *, search: Optional[str] = None, limit: int = 50, offset: int = 0, user_id: Optional[str] = None):
        return self.repo.list(search=search, limit=limit, offset=offset, user_id=user_id)

    @transaction.atomic
    def create(self, *, user_id: str, module_id: str, permission_name: str, **attrs) -> UserPermission:
        if not user_id or not module_id or not permission_name:
            raise ValueError("user_id, module_id, and permission_name are required")
        return self.repo.create(user_id=user_id, module_id=module_id, permission_name=permission_name, **attrs)

    @transaction.atomic
    def update(self, permission_id: str, **attrs) -> UserPermission:
        permission = self.repo.get_by_id(permission_id)
        if not permission:
            raise ValueError("UserPermission not found")
        return self.repo.update(permission, **attrs)



