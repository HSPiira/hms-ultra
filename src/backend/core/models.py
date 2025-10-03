from django.db import models
from cuid2 import Cuid


def generate_cuid() -> str:
    return Cuid().generate()


class CuidModel(models.Model):
    id = models.CharField(primary_key=True, max_length=27, default=generate_cuid, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    DELETED = 'DELETED', 'Deleted'


class YesNoChoices(models.TextChoices):
    YES = 'YES', 'Yes'
    NO = 'NO', 'No'


class CompanyType(CuidModel, TimeStampedModel):
    type_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_company_types'


class Company(CuidModel, TimeStampedModel):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    company_address = models.CharField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=200, blank=True)
    remarks = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    district_id = models.IntegerField(null=True, blank=True)
    currentupdate = models.CharField(max_length=20, default='ACTIVE')
    company_type = models.ForeignKey(CompanyType, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'nm_companies'


class CompanyBranch(CuidModel, TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=200, blank=True)
    branch_address = models.CharField(max_length=500, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_company_branches'


class Scheme(CuidModel, TimeStampedModel):
    scheme_name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    limit_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    familystatus = models.IntegerField(default=0)
    beginningdate = models.DateField()
    endingdate = models.DateField()
    terminationdate = models.DateField(null=True, blank=True)
    termination = models.IntegerField(default=0)
    numberofdays = models.IntegerField(null=True, blank=True)
    card_code = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'nm_schemes'


class Plan(CuidModel, TimeStampedModel):
    planname = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_plans'


class SchemePlan(CuidModel, TimeStampedModel):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    copayment_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_scheme_plans'
        constraints = [
            models.UniqueConstraint(fields=['scheme', 'plan'], name='uq_scheme_plan')
        ]


class Benefit(CuidModel, TimeStampedModel):
    service_name = models.CharField(max_length=200)
    in_or_out_patient = models.CharField(max_length=20, blank=True)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    scheme_duration = models.IntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=500, blank=True)
    covered = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.YES)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_benefits'


class SchemeBenefit(CuidModel, TimeStampedModel):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    scheme_benefit = models.ForeignKey(Benefit, on_delete=models.PROTECT)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    copayment_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waiting_period_days = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_scheme_benefits'
        constraints = [
            models.UniqueConstraint(fields=['scheme', 'scheme_benefit'], name='uq_scheme_benefit')
        ]


class Member(CuidModel, TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    scheme = models.ForeignKey(Scheme, on_delete=models.PROTECT)
    member_name = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=50, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    postal_address = models.CharField(max_length=500, blank=True)
    physical_address = models.CharField(max_length=500, blank=True)
    phone_home = models.CharField(max_length=50, blank=True)
    phone_mobile = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=50, blank=True)
    card_number = models.CharField(max_length=50, unique=True)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    member_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    photo_path = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'nm_members'


class MemberDependant(CuidModel, TimeStampedModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    dependant_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    bloodgroup = models.CharField(max_length=5, blank=True)
    postal_address = models.CharField(max_length=500, blank=True)
    telhome = models.CharField(max_length=50, blank=True)
    telmobile = models.CharField(max_length=50, blank=True)
    nextofkin = models.CharField(max_length=200, blank=True)
    depcardno = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    dateformrecieved = models.DateField(null=True, blank=True)
    datephotorecieved = models.DateField(null=True, blank=True)
    datecardrecieved = models.DateField(null=True, blank=True)
    datephotosenttoinsurer = models.DateField(null=True, blank=True)
    datecardsenttoclient = models.DateField(null=True, blank=True)
    cardorphotocomment = models.CharField(max_length=500, blank=True)
    cardstatus = models.CharField(max_length=50, blank=True)
    photostatus = models.CharField(max_length=50, blank=True)

    dateofjoining = models.DateField(null=True, blank=True)
    dateofleaving = models.DateField(null=True, blank=True)
    dateofstate = models.DateField(null=True, blank=True)
    dateofend = models.DateField(null=True, blank=True)

    dimage = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'nm_members_dependants'


class Hospital(CuidModel, TimeStampedModel):
    hospital_reference = models.CharField(max_length=50, unique=True)
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.CharField(max_length=500, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    outpatient_capacity = models.IntegerField(null=True, blank=True)
    inpatient_capacity = models.IntegerField(null=True, blank=True)
    district_id = models.IntegerField(null=True, blank=True)
    hospital_email = models.CharField(max_length=100, blank=True)
    hospital_website = models.CharField(max_length=200, blank=True)
    hospital_remarks = models.CharField(max_length=500, blank=True)
    hospital_phone_number = models.CharField(max_length=50, blank=True)
    outorinpatient = models.CharField(max_length=20, blank=True)
    dental = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.NO)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_by = models.CharField(max_length=100, blank=True)  # User who created/owns this hospital

    class Meta:
        db_table = 'nm_hospitals'


class HospitalStaff(CuidModel, TimeStampedModel):
    """Model for hospital staff associations"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='hospital_staff')
    role = models.CharField(max_length=50, default='STAFF')  # STAFF, ADMIN, MANAGER, etc.
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    notes = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'nm_hospital_staff'
        constraints = [
            models.UniqueConstraint(fields=['hospital', 'user'], name='uq_hospital_user_staff')
        ]


class HospitalBranch(CuidModel, TimeStampedModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    hospital_branchname = models.CharField(max_length=200, blank=True)
    branch_address = models.CharField(max_length=500, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_hospital_branches'


class HospitalDoctor(CuidModel, TimeStampedModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    doctorname = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_hospital_doctors'


class Medicine(CuidModel, TimeStampedModel):
    medicineid = models.CharField(max_length=50, unique=True)
    medicinereferenceno = models.CharField(max_length=100, blank=True)
    medicinename = models.CharField(max_length=200)
    dosageform = models.CharField(max_length=100, blank=True)
    unitprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unitsinstock = models.BigIntegerField(null=True, blank=True)
    reorderlevel = models.BigIntegerField(null=True, blank=True)
    additionalnotes = models.CharField(max_length=500, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_medicines'


class HospitalMedicine(CuidModel, TimeStampedModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.YES)
    effective_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_hospital_medicines'
        constraints = [
            models.UniqueConstraint(fields=['hospital', 'medicine'], name='uq_hospital_medicine')
        ]


class Service(CuidModel, TimeStampedModel):
    service_code = models.CharField(max_length=50, unique=True, blank=True)
    service_name = models.CharField(max_length=200)
    service_category = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)
    base_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    service_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_services'


class HospitalService(CuidModel, TimeStampedModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    available = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.YES)
    effective_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_hospital_services'
        constraints = [
            models.UniqueConstraint(fields=['hospital', 'service'], name='uq_hospital_service')
        ]


class LabTest(CuidModel, TimeStampedModel):
    test_code = models.CharField(max_length=50, unique=True)
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)
    base_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    normal_range = models.CharField(max_length=200, blank=True)
    units = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_lab_tests'


class HospitalLabTest(CuidModel, TimeStampedModel):
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    labtest = models.ForeignKey(LabTest, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    available = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.YES)
    turnaround_hours = models.IntegerField(null=True, blank=True)
    effective_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_hospital_labtests'
        constraints = [
            models.UniqueConstraint(fields=['hospital', 'labtest'], name='uq_hospital_labtest')
        ]


class Diagnosis(CuidModel, TimeStampedModel):
    icd10_code = models.CharField(max_length=20, unique=True)
    who_short_descr = models.CharField(max_length=200)
    who_full_descr = models.CharField(max_length=1000, blank=True)
    icd_3code = models.BigIntegerField(null=True, blank=True)
    icd_3code_desc = models.CharField(max_length=200, blank=True)
    chronicflag = models.CharField(max_length=10, choices=YesNoChoices.choices, default=YesNoChoices.NO)
    group_code = models.BigIntegerField(null=True, blank=True)
    group_description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_diagnosis'


class Claim(CuidModel, TimeStampedModel):
    transid = models.BigIntegerField(null=True, blank=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    member_name = models.CharField(max_length=200, blank=True)
    cardno = models.CharField(max_length=50, blank=True)
    dependant = models.ForeignKey(MemberDependant, null=True, blank=True, on_delete=models.PROTECT)
    dependant_name = models.CharField(max_length=200, blank=True)
    transaction_date = models.DateField(auto_now_add=True)
    doctor = models.ForeignKey(HospitalDoctor, null=True, blank=True, on_delete=models.PROTECT)
    doctorname = models.CharField(max_length=200, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    hospital_name = models.CharField(max_length=200, blank=True)
    hospital_branch = models.ForeignKey(HospitalBranch, null=True, blank=True, on_delete=models.PROTECT)
    hospital_branchname = models.CharField(max_length=200, blank=True)
    service_date = models.DateField()
    servicetype = models.CharField(max_length=50, blank=True)
    outorinpatienttransaction = models.CharField(max_length=20, blank=True)
    hospital_claimamount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    member_claimamount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    amountpaid = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    claimform_number = models.CharField(max_length=100, blank=True)
    claimref = models.BigIntegerField(null=True, blank=True)
    claimformserialnumber = models.CharField(max_length=100, blank=True)
    dateofsubmission = models.DateField(null=True, blank=True)
    claimformcomments = models.CharField(max_length=1000, blank=True)
    claimquarantine = models.IntegerField(default=0)
    approved = models.IntegerField(default=0)
    lateclaimform = models.IntegerField(default=0)
    billingsessionid = models.BigIntegerField(null=True, blank=True)
    chequenumbers = models.CharField(max_length=200, blank=True)
    transpaid = models.CharField(max_length=20, default='NO')
    transaction_status = models.CharField(max_length=50, default='PENDING')
    username = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'nm_claims'
        indexes = [
            models.Index(fields=['member']),
            models.Index(fields=['hospital']),
            models.Index(fields=['service_date']),
            models.Index(fields=['transaction_status']),
        ]


class ClaimDetail(CuidModel, TimeStampedModel):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    transid = models.BigIntegerField(null=True, blank=True)
    transaction_date = models.DateField(null=True, blank=True)
    trans_type = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    comments = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=50, default='PENDING')
    allowed = models.IntegerField(default=1)
    chronic = models.IntegerField(default=0)

    class Meta:
        db_table = 'nm_claim_details'


class ClaimPayment(CuidModel, TimeStampedModel):
    claim = models.ForeignKey(Claim, on_delete=models.PROTECT)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    cheque_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(max_length=50, default='PENDING')
    remarks = models.CharField(max_length=500, blank=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'nm_claim_payments'


class BillingSession(CuidModel, TimeStampedModel):
    session_name = models.CharField(max_length=200, blank=True)
    session_date = models.DateField(auto_now_add=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    total_claims = models.BigIntegerField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    session_status = models.CharField(max_length=50, default='OPEN')
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'nm_billing_sessions'


class District(CuidModel, TimeStampedModel):
    district_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_districts'


class FinancialPeriod(CuidModel, TimeStampedModel):
    period_name = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_financial_periods'


class ApplicationUser(CuidModel, TimeStampedModel):
    empid = models.BigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=500)
    lastlogin = models.DateField(null=True, blank=True)
    updatedate = models.DateField(null=True, blank=True)
    account_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    password_expires = models.DateField(null=True, blank=True)
    failed_attempts = models.IntegerField(default=0)

    class Meta:
        db_table = 'nm_application_users'


class ApplicationModule(CuidModel, TimeStampedModel):
    module_code = models.CharField(max_length=50, unique=True)
    module_name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    parent_module_id = models.BigIntegerField(null=True, blank=True)
    module_order = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'nm_application_modules'


class UserPermission(CuidModel, TimeStampedModel):
    user = models.ForeignKey(ApplicationUser, on_delete=models.CASCADE)
    module = models.ForeignKey(ApplicationModule, on_delete=models.CASCADE)
    can_view = models.IntegerField(default=0)
    can_create = models.IntegerField(default=0)
    can_edit = models.IntegerField(default=0)
    can_delete = models.IntegerField(default=0)
    can_approve = models.IntegerField(default=0)
    granted_by = models.BigIntegerField(null=True, blank=True)
    granted_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'nm_user_permissions'
        constraints = [
            models.UniqueConstraint(fields=['user', 'module'], name='uq_user_module_permission')
        ]
