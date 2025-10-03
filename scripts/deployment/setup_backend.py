#!/usr/bin/env python
"""
HMS Backend Setup Script
Creates essential data for the Hospital Management System
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_ultra.settings')
django.setup()

from core.models import (
    CompanyType, Plan, Benefit, Medicine, Service, LabTest, 
    Diagnosis, District, FinancialPeriod, ApplicationModule
)

def create_company_types():
    """Create essential company types"""
    print("Creating company types...")
    company_types = [
        ('Insurance Company', 'Health insurance providers'),
        ('Corporate Client', 'Corporate health schemes'),
        ('Government Agency', 'Government health programs'),
        ('Healthcare Provider', 'Hospitals and clinics'),
        ('Third Party Administrator', 'TPA services')
    ]
    
    for name, description in company_types:
        CompanyType.objects.get_or_create(
            type_name=name,
            defaults={'description': description}
        )
    print(f"✓ Created {len(company_types)} company types")

def create_plans():
    """Create basic insurance plans"""
    print("Creating plans...")
    plans = [
        ('Basic Plan', 'Basic health coverage with essential benefits'),
        ('Premium Plan', 'Comprehensive health coverage with extended benefits'),
        ('Family Plan', 'Family health coverage for multiple members'),
        ('Corporate Plan', 'Corporate health coverage for employees'),
        ('Student Plan', 'Health coverage for students and young adults')
    ]
    
    for name, description in plans:
        Plan.objects.get_or_create(
            planname=name,
            defaults={'description': description}
        )
    print(f"✓ Created {len(plans)} plans")

def create_benefits():
    """Create essential benefits"""
    print("Creating benefits...")
    benefits = [
        ('General Consultation', 'OUTPATIENT', 2000.00, 'General medical consultation'),
        ('Specialist Consultation', 'OUTPATIENT', 5000.00, 'Specialist medical consultation'),
        ('Emergency Treatment', 'BOTH', 10000.00, 'Emergency medical treatment'),
        ('Surgery', 'INPATIENT', 50000.00, 'Surgical procedures'),
        ('Laboratory Tests', 'OUTPATIENT', 3000.00, 'Medical laboratory tests'),
        ('Imaging', 'OUTPATIENT', 8000.00, 'X-ray, MRI, CT scans'),
        ('Pharmacy', 'OUTPATIENT', 1000.00, 'Prescription medications'),
        ('Maternity', 'BOTH', 30000.00, 'Maternity and delivery services'),
        ('Dental', 'OUTPATIENT', 5000.00, 'Dental care and treatment'),
        ('Optical', 'OUTPATIENT', 3000.00, 'Eye care and vision services')
    ]
    
    for name, patient_type, limit, desc in benefits:
        Benefit.objects.get_or_create(
            service_name=name,
            defaults={
                'in_or_out_patient': patient_type,
                'limit_amount': limit,
                'remarks': desc
            }
        )
    print(f"✓ Created {len(benefits)} benefits")

def create_medicines():
    """Create medicine catalog"""
    print("Creating medicines...")
    medicines = [
        ('MED001', 'Paracetamol 500mg', 'Tablet', 5.00, 1000, 100, 'Pain relief medication'),
        ('MED002', 'Amoxicillin 250mg', 'Capsule', 15.00, 500, 50, 'Antibiotic for bacterial infections'),
        ('MED003', 'Ibuprofen 400mg', 'Tablet', 8.00, 800, 80, 'Anti-inflammatory pain relief'),
        ('MED004', 'Omeprazole 20mg', 'Capsule', 25.00, 300, 30, 'Proton pump inhibitor for acid reflux'),
        ('MED005', 'Metformin 500mg', 'Tablet', 12.00, 400, 40, 'Diabetes medication'),
        ('MED006', 'Amlodipine 5mg', 'Tablet', 18.00, 350, 35, 'Blood pressure medication'),
        ('MED007', 'Lisinopril 10mg', 'Tablet', 20.00, 300, 30, 'ACE inhibitor for hypertension'),
        ('MED008', 'Atorvastatin 20mg', 'Tablet', 30.00, 250, 25, 'Cholesterol lowering medication'),
        ('MED009', 'Metronidazole 400mg', 'Tablet', 22.00, 200, 20, 'Antibiotic for anaerobic infections'),
        ('MED010', 'Ciprofloxacin 500mg', 'Tablet', 35.00, 150, 15, 'Broad spectrum antibiotic')
    ]
    
    for med_id, name, form, price, stock, reorder, notes in medicines:
        Medicine.objects.get_or_create(
            medicineid=med_id,
            defaults={
                'medicinename': name,
                'dosageform': form,
                'unitprice': price,
                'unitsinstock': stock,
                'reorderlevel': reorder,
                'additionalnotes': notes
            }
        )
    print(f"✓ Created {len(medicines)} medicines")

def create_services():
    """Create medical services"""
    print("Creating services...")
    services = [
        ('SVC001', 'General Consultation', 'Consultation', 2000.00, 'OUTPATIENT'),
        ('SVC002', 'Specialist Consultation', 'Consultation', 5000.00, 'OUTPATIENT'),
        ('SVC003', 'Emergency Treatment', 'Emergency', 10000.00, 'BOTH'),
        ('SVC004', 'Minor Surgery', 'Surgery', 25000.00, 'INPATIENT'),
        ('SVC005', 'Major Surgery', 'Surgery', 100000.00, 'INPATIENT'),
        ('SVC006', 'Dental Cleaning', 'Dental', 3000.00, 'OUTPATIENT'),
        ('SVC007', 'Eye Examination', 'Optical', 2500.00, 'OUTPATIENT'),
        ('SVC008', 'Physiotherapy', 'Rehabilitation', 4000.00, 'OUTPATIENT'),
        ('SVC009', 'Maternity Care', 'Maternity', 15000.00, 'BOTH'),
        ('SVC010', 'Pediatric Care', 'Pediatrics', 3500.00, 'OUTPATIENT')
    ]
    
    for svc_code, name, category, amount, svc_type in services:
        Service.objects.get_or_create(
            service_code=svc_code,
            defaults={
                'service_name': name,
                'service_category': category,
                'base_amount': amount,
                'service_type': svc_type
            }
        )
    print(f"✓ Created {len(services)} services")

def create_lab_tests():
    """Create laboratory tests"""
    print("Creating lab tests...")
    lab_tests = [
        ('LAB001', 'Complete Blood Count', 'Hematology', 1500.00, '4.5-11.0 x 10^9/L', 'cells/L'),
        ('LAB002', 'Blood Sugar (Fasting)', 'Biochemistry', 800.00, '3.9-5.5 mmol/L', 'mmol/L'),
        ('LAB003', 'Lipid Profile', 'Biochemistry', 2500.00, 'Cholesterol <5.2 mmol/L', 'mmol/L'),
        ('LAB004', 'Liver Function Tests', 'Biochemistry', 3000.00, 'ALT <40 U/L', 'U/L'),
        ('LAB005', 'Kidney Function Tests', 'Biochemistry', 2000.00, 'Creatinine <106 μmol/L', 'μmol/L'),
        ('LAB006', 'Thyroid Function Tests', 'Endocrinology', 4000.00, 'TSH 0.4-4.0 mIU/L', 'mIU/L'),
        ('LAB007', 'Urine Analysis', 'Urinalysis', 1000.00, 'Normal range', 'Various'),
        ('LAB008', 'Stool Analysis', 'Microbiology', 1200.00, 'Normal range', 'Various'),
        ('LAB009', 'Blood Group & Rh', 'Immunology', 800.00, 'A, B, AB, O', 'Blood Type'),
        ('LAB010', 'HIV Test', 'Serology', 2000.00, 'Negative', 'Qualitative')
    ]
    
    for test_code, name, category, amount, normal_range, units in lab_tests:
        LabTest.objects.get_or_create(
            test_code=test_code,
            defaults={
                'test_name': name,
                'test_category': category,
                'base_amount': amount,
                'normal_range': normal_range,
                'units': units
            }
        )
    print(f"✓ Created {len(lab_tests)} lab tests")

def create_diagnoses():
    """Create common diagnoses"""
    print("Creating diagnoses...")
    diagnoses = [
        ('A00', 'Cholera', 'Acute diarrheal infection caused by Vibrio cholerae', 'NO'),
        ('A09', 'Diarrhea and gastroenteritis', 'Infectious diarrhea and gastroenteritis', 'NO'),
        ('B34.9', 'Viral infection, unspecified', 'Viral infection not otherwise specified', 'NO'),
        ('C78.00', 'Secondary malignant neoplasm of unspecified lung', 'Metastatic cancer to lung', 'YES'),
        ('D50.9', 'Iron deficiency anemia, unspecified', 'Iron deficiency anemia', 'YES'),
        ('E11.9', 'Type 2 diabetes mellitus without complications', 'Type 2 diabetes mellitus', 'YES'),
        ('F32.9', 'Major depressive disorder, single episode, unspecified', 'Depression', 'YES'),
        ('G43.9', 'Migraine, unspecified', 'Migraine headache', 'NO'),
        ('H10.9', 'Conjunctivitis, unspecified', 'Eye inflammation', 'NO'),
        ('I10', 'Essential hypertension', 'High blood pressure', 'YES')
    ]
    
    for icd10, short_desc, full_desc, chronic in diagnoses:
        Diagnosis.objects.get_or_create(
            icd10_code=icd10,
            defaults={
                'who_short_descr': short_desc,
                'who_full_descr': full_desc,
                'chronicflag': chronic
            }
        )
    print(f"✓ Created {len(diagnoses)} diagnoses")

def create_districts():
    """Create districts"""
    print("Creating districts...")
    districts = [
        ('Nairobi', 'Central', 'KE'),
        ('Mombasa', 'Coast', 'KE'),
        ('Kisumu', 'Nyanza', 'KE'),
        ('Nakuru', 'Rift Valley', 'KE'),
        ('Eldoret', 'Rift Valley', 'KE')
    ]
    
    for name, region, country in districts:
        District.objects.get_or_create(
            district_name=name,
            defaults={
                'region': region,
                'country_code': country
            }
        )
    print(f"✓ Created {len(districts)} districts")

def create_financial_periods():
    """Create financial periods"""
    print("Creating financial periods...")
    from datetime import date
    
    periods = [
        ('2024 Q1', date(2024, 1, 1), date(2024, 3, 31), False),
        ('2024 Q2', date(2024, 4, 1), date(2024, 6, 30), False),
        ('2024 Q3', date(2024, 7, 1), date(2024, 9, 30), False),
        ('2024 Q4', date(2024, 10, 1), date(2024, 12, 31), True),
        ('2025 Q1', date(2025, 1, 1), date(2025, 3, 31), False)
    ]
    
    for name, start, end, current in periods:
        FinancialPeriod.objects.get_or_create(
            period_name=name,
            defaults={
                'start_date': start,
                'end_date': end,
                'is_current': 1 if current else 0
            }
        )
    print(f"✓ Created {len(periods)} financial periods")

def create_application_modules():
    """Create application modules"""
    print("Creating application modules...")
    modules = [
        ('MEMBERS', 'Member Management', 'Manage members and dependants'),
        ('COMPANIES', 'Company Management', 'Manage companies and branches'),
        ('SCHEMES', 'Scheme Management', 'Manage insurance schemes'),
        ('HOSPITALS', 'Hospital Management', 'Manage hospitals and providers'),
        ('CLAIMS', 'Claims Processing', 'Process and manage claims'),
        ('REPORTS', 'Reports & Analytics', 'Generate reports and analytics'),
        ('ADMIN', 'System Administration', 'System administration and settings'),
        ('BILLING', 'Billing Management', 'Manage billing and payments')
    ]
    
    for code, name, description in modules:
        ApplicationModule.objects.get_or_create(
            module_code=code,
            defaults={
                'module_name': name,
                'description': description
            }
        )
    print(f"✓ Created {len(modules)} application modules")

def main():
    """Run the complete setup"""
    print("🚀 Starting HMS Backend Setup...")
    print("=" * 50)
    
    try:
        create_company_types()
        create_plans()
        create_benefits()
        create_medicines()
        create_services()
        create_lab_tests()
        create_diagnoses()
        create_districts()
        create_financial_periods()
        create_application_modules()
        
        print("=" * 50)
        print("✅ HMS Backend Setup Complete!")
        print("🎉 All essential data has been created.")
        print("\nNext steps:")
        print("1. Test the APIs using Postman")
        print("2. Create companies, schemes, and hospitals")
        print("3. Add members and process claims")
        print("4. Configure production settings")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
