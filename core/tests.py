from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from .models import Company, Scheme, Member, Hospital
from .repositories import DjangoMemberRepository
from .services import MemberService, MemberCreateDTO


class MemberServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(company_name="Acme")
        self.scheme = Scheme.objects.create(
            scheme_name="Gold",
            company=self.company,
            beginningdate="2024-01-01",
            endingdate="2025-01-01",
        )
        self.repo = DjangoMemberRepository()
        self.service = MemberService(self.repo)

    def test_create_member(self):
        dto = MemberCreateDTO(
            member_name="John Doe",
            company_id=self.company.id,
            scheme_id=self.scheme.id,
            card_number="CARD123",
        )
        member = self.service.create_member(dto)
        self.assertIsNotNone(member.id)
        self.assertEqual(member.member_name, "John Doe")


class SchemeAndHospitalAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.company = Company.objects.create(company_name="Acme")

    def _auth(self):
        resp = self.client.post("/api/token/", {"username": "tester", "password": "pass12345"}, format="json")
        self.assertEqual(resp.status_code, 200)
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_scheme_crud(self):
        self._auth()
        payload = {
            "scheme_name": "Silver",
            "company": self.company.id,
            "beginningdate": "2025-01-01",
            "endingdate": "2026-01-01",
        }
        resp = self.client.post("/api/schemes/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        scheme_id = resp.data["id"]
        # List
        resp = self.client.get("/api/schemes/?company=" + self.company.id)
        self.assertEqual(resp.status_code, 200)
        # Update
        resp = self.client.put(f"/api/schemes/{scheme_id}/", {"description": "desc"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_hospital_crud(self):
        self._auth()
        payload = {
            "hospital_reference": "H001",
            "hospital_name": "City Hospital",
            "hospital_phone_number": "+254700000000",
        }
        resp = self.client.post("/api/hospitals/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        hospital_id = resp.data["id"]
        # List
        resp = self.client.get("/api/hospitals/?search=City")
        self.assertEqual(resp.status_code, 200)
        # Update
        resp = self.client.put(f"/api/hospitals/{hospital_id}/", {"contact_person": "Admin"}, format="json")
        self.assertEqual(resp.status_code, 200)


class MemberAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.company = Company.objects.create(company_name="Acme")
        self.scheme = Scheme.objects.create(
            scheme_name="Gold",
            company=self.company,
            beginningdate="2024-01-01",
            endingdate="2025-01-01",
        )
        # Use session auth bypass for tests by force_authenticate via DRF if we add users later

    def test_member_list_unauthenticated(self):
        resp = self.client.get("/api/members/")
        self.assertEqual(resp.status_code, 401)

    def test_member_crud_authenticated(self):
        # Obtain JWT
        resp = self.client.post("/api/token/", {"username": "tester", "password": "pass12345"}, format="json")
        self.assertEqual(resp.status_code, 200)
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Create member
        payload = {
            "member_name": "Jane Roe",
            "company": self.company.id,
            "scheme": self.scheme.id,
            "card_number": "CARD999",
        }
        resp = self.client.post("/api/members/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        member_id = resp.data["id"]

        # Retrieve
        resp = self.client.get(f"/api/members/{member_id}/")
        self.assertEqual(resp.status_code, 200)

        # Update
        resp = self.client.put(f"/api/members/{member_id}/", {"phone_mobile": "+123"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["phone_mobile"], "+123")

        # Activate
        resp = self.client.post(f"/api/members/{member_id}/activate/")
        self.assertEqual(resp.status_code, 200)

        # Deactivate
        resp = self.client.post(f"/api/members/{member_id}/deactivate/")
        self.assertEqual(resp.status_code, 200)

# Create your tests here.
