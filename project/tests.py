from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company
from role.models import Role
from project.models import Project, ProjectStatus, ProjectPriority

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Alpha Corp",
            code="ALPHA",
            email="alpha@example.com"
        )
        self.project = Project.objects.create(
            company=self.company,
            name="EMS Portal",
            code="PRJ-001",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            budget=50000.00
        )

    def test_project_creation(self):
        self.assertEqual(self.project.name, "EMS Portal")
        self.assertEqual(self.project.code, "PRJ-001")
        self.assertEqual(self.project.status, ProjectStatus.ACTIVE)
        self.assertEqual(self.project.priority, ProjectPriority.HIGH)
        self.assertEqual(str(self.project), "EMS Portal (PRJ-001)")


class ProjectAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Beta Corp",
            code="BETA",
            email="beta@example.com"
        )
        self.role = Role.objects.create(
            name="Manager"
        )
        self.user = User.objects.create_user(
            username="projectuser",
            password="password123",
            email="puser@example.com",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            company=self.company,
            name="CRM System",
            code="CRM-100",
            status=ProjectStatus.PLANNED,
            priority=ProjectPriority.MEDIUM,
            budget=25000.00
        )

        self.list_create_url = reverse("project-list-create")
        self.detail_url = reverse("project-detail", kwargs={"pk": self.project.pk})

    def test_list_projects(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_create_project_success(self):
        payload = {
            "company": self.company.id,
            "name": "Mobile App",
            "code": "MAP-200",
            "description": "Cross-platform mobile application",
            "status": "ACTIVE",
            "priority": "HIGH",
            "budget": "15000.00"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["code"], "MAP-200")

    def test_create_project_duplicate_code_fails(self):
        payload = {
            "company": self.company.id,
            "name": "Duplicate Project",
            "code": "CRM-100",
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_retrieve_project(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "CRM System")

    def test_update_project(self):
        payload = {
            "company": self.company.id,
            "name": "Updated CRM System",
            "code": "CRM-100",
            "status": "COMPLETED",
            "priority": "CRITICAL",
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Updated CRM System")
        self.assertEqual(response.data["data"]["status"], "COMPLETED")

    def test_delete_project(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
