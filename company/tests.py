from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Company
from role.models import Role

User = get_user_model()


class CompanyModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="TechCorp",
            code="TC001",
            email="info@techcorp.com",
            phone="+1234567890",
            website="https://techcorp.com",
            address="123 Tech St",
            city="Techville",
            state="TechState",
            country="Techland",
            is_active=True
        )

    def test_company_creation(self):
        self.assertEqual(self.company.name, "TechCorp")
        self.assertEqual(self.company.code, "TC001")
        self.assertTrue(self.company.is_active)
        self.assertEqual(str(self.company), "TechCorp (TC001)")


class CompanyAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_company = Company.objects.create(
            name="User Corp",
            code="UC001",
            email="usercorp@example.com"
        )
        self.user_role = Role.objects.create(
            company=self.user_company,
            name="Admin Role"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="user@example.com",
            role=self.user_role,
            company=self.user_company
        )
        self.client.force_authenticate(user=self.user)
        self.company = Company.objects.create(
            name="Acme Inc",
            code="ACME",
            email="contact@acme.com"
        )
        self.list_create_url = reverse("company-list-create")
        self.detail_url = reverse("company-detail", kwargs={"pk": self.company.pk})

    def test_list_companies(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)

    def test_list_companies_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)

    def test_create_company_unauthenticated(self):
        unauthenticated_client = APIClient()
        payload = {
            "name": "Unauthorized Inc",
            "code": "UNAUTH01",
        }
        response = unauthenticated_client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_company_success(self):
        payload = {
            "name": "Global Logistics",
            "code": "GLOG",
            "email": "info@glog.com",
            "phone": "9876543210",
            "website": "https://glog.com",
            "city": "Metropolis",
            "country": "USA"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["code"], "GLOG")

    def test_create_company_duplicate_code_fails(self):
        payload = {
            "name": "Acme Duplicate",
            "code": "ACME",
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_retrieve_company(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Acme Inc")

    def test_update_company(self):
        payload = {
            "name": "Acme Corporation",
            "code": "ACME",
            "email": "updated@acme.com"
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Acme Corporation")
        self.assertEqual(response.data["data"]["email"], "updated@acme.com")

    def test_delete_company(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Company.objects.filter(pk=self.company.pk).exists())
