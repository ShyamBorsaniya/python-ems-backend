from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company
from role.models import Role
from .models import Department

User = get_user_model()


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="TechCorp",
            code="TC001"
        )
        self.role = Role.objects.create(
            company=self.company,
            name="Manager Role"
        )
        self.user = User.objects.create_user(
            username="manager1",
            email="manager1@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering",
            description="Software and Hardware engineering",
            manager=self.user,
            is_active=True
        )

    def test_department_creation(self):
        self.assertEqual(self.department.name, "Engineering")
        self.assertEqual(self.department.company, self.company)
        self.assertEqual(self.department.manager, self.user)
        self.assertTrue(self.department.is_active)
        self.assertEqual(str(self.department), "Engineering (TechCorp)")


class DepartmentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Acme Inc",
            code="ACME"
        )
        self.role = Role.objects.create(
            company=self.company,
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
        self.department = Department.objects.create(
            company=self.company,
            name="Human Resources",
            description="HR Department"
        )
        self.list_create_url = reverse("department-list-create")
        self.detail_url = reverse("department-detail", kwargs={"pk": self.department.pk})

    def test_list_departments(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_create_department_success(self):
        payload = {
            "company": self.company.id,
            "name": "Finance",
            "description": "Finance and Accounting",
            "manager": self.user.id,
            "is_active": True
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Finance")

    def test_retrieve_department(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Human Resources")

    def test_update_department(self):
        payload = {
            "company": self.company.id,
            "name": "People Operations",
            "description": "Updated HR Dept",
            "is_active": True
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "People Operations")

    def test_partial_update_department(self):
        payload = {
            "name": "Global HR"
        }
        response = self.client.patch(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Global HR")

    def test_delete_department(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Department.objects.filter(pk=self.department.pk).exists())
