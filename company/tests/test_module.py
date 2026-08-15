from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company, Role, Module

User = get_user_model()


class ModuleModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="TechCorp",
            code="TC001"
        )
        self.module = Module.objects.create(
            company=self.company,
            name="leave_mgmt",
            display_name="Leave Management",
            code="LM001",
            description="Manage employee leave requests",
            is_active=True
        )

    def test_module_creation(self):
        self.assertEqual(self.module.name, "leave_mgmt")
        self.assertEqual(self.module.display_name, "Leave Management")
        self.assertEqual(self.module.code, "LM001")
        self.assertEqual(self.module.company, self.company)
        self.assertTrue(self.module.is_active)
        self.assertEqual(str(self.module), "Leave Management (LM001)")


class ModuleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Acme Inc",
            code="ACME",
            email="info@acme.com",
            phone="1234567890",
            website="https://acme.com"
        )
        self.role = Role.objects.create(
            name="Admin Role"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="user@example.com",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.module = Module.objects.create(
            company=self.company,
            name="payroll",
            display_name="Payroll Management",
            code="PR001",
            description="Process employee salaries"
        )
        self.list_create_url = reverse("module-list-create")
        self.detail_url = reverse("module-detail", kwargs={"pk": self.module.pk})

    def test_list_modules(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_full_company_record_in_serializer(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_data = response.data["data"]["company"]
        self.assertIsNotNone(company_data)
        self.assertIsInstance(company_data, dict)
        self.assertEqual(company_data["id"], self.company.id)
        self.assertEqual(company_data["name"], "Acme Inc")
        self.assertEqual(company_data["code"], "ACME")
        self.assertEqual(company_data["email"], "info@acme.com")

    def test_create_module_with_company(self):
        payload = {
            "company": self.company.id,
            "name": "project_mgmt",
            "display_name": "Project Management",
            "code": "PM001",
            "description": "Manage client projects",
            "is_active": True
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["display_name"], "Project Management")
        self.assertEqual(response.data["data"]["code"], "PM001")
        # Verify full company object is returned in serializer response
        self.assertEqual(response.data["data"]["company"]["name"], "Acme Inc")

    def test_create_global_module_without_company(self):
        payload = {
            "company": None,
            "name": "global_analytics",
            "display_name": "Global Analytics",
            "code": "GA001",
            "description": "Platform wide analytics",
            "is_active": True
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["data"]["company"])

    def test_create_module_duplicate_code_same_company_fails(self):
        payload = {
            "company": self.company.id,
            "name": "another_payroll",
            "display_name": "Duplicate Payroll",
            "code": "PR001"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_search_module_by_name_or_code(self):
        response = self.client.get(f"{self.list_create_url}?search=payroll")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["name"], "payroll")

    def test_update_module(self):
        payload = {
            "company": self.company.id,
            "name": "payroll_v2",
            "display_name": "Payroll Management V2",
            "code": "PR002",
            "description": "Updated description",
            "is_active": True
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["display_name"], "Payroll Management V2")

    def test_partial_update_module(self):
        payload = {
            "display_name": "Advanced Payroll"
        }
        response = self.client.patch(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["display_name"], "Advanced Payroll")

    def test_delete_module(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Module.objects.filter(pk=self.module.pk).exists())
