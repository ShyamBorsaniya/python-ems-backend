from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from company.models import (
    Company, Role, User, Employee, Project, ProjectMember,
    ProjectStatus, ProjectPriority
)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Alpha Corp",
            code="ALPHA"
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


class ProjectMemberAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Gamma Corp",
            code="GAMMA",
            email="gamma@example.com"
        )
        self.role = Role.objects.create(name="Dev Lead")
        self.user = User.objects.create_user(
            username="assignuser",
            password="password123",
            email="auser@example.com",
            role=self.role,
            company=self.company
        )
        self.emp_user = User.objects.create_user(
            username="employeeuser",
            password="password123",
            email="jane.doe@example.com",
            first_name="Jane",
            last_name="Doe",
            role=self.role,
            company=self.company
        )
        self.employee = Employee.objects.create(
            user=self.emp_user,
            company=self.company,
            code="EMP-001",
            joining_date="2024-01-01"
        )
        self.project = Project.objects.create(
            company=self.company,
            name="AI Platform",
            code="AIP-100",
            status=ProjectStatus.ACTIVE
        )
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("project-member-list-create")

    def test_create_project_member_success(self):
        payload = {
            "project": self.project.id,
            "employee": self.employee.id,
            "role_in_project": "Tech Lead"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["role_in_project"], "Tech Lead")

    def test_duplicate_project_member_fails(self):
        ProjectMember.objects.create(
            project=self.project,
            employee=self.employee,
            role_in_project="QA"
        )
        payload = {
            "project": self.project.id,
            "employee": self.employee.id,
            "role_in_project": "Developer"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_list_and_filter_project_members(self):
        member = ProjectMember.objects.create(
            project=self.project,
            employee=self.employee,
            role_in_project="Tech Lead"
        )
        response = self.client.get(f"{self.list_create_url}?project={self.project.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["id"], member.id)

    def test_retrieve_update_delete_project_member(self):
        member = ProjectMember.objects.create(
            project=self.project,
            employee=self.employee,
            role_in_project="Developer"
        )
        detail_url = reverse("project-member-detail", kwargs={"pk": member.pk})

        # GET
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["role_in_project"], "Developer")

        # PATCH
        patch_res = self.client.patch(detail_url, {"role_in_project": "Senior Developer"})
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["data"]["role_in_project"], "Senior Developer")

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(ProjectMember.objects.filter(pk=member.pk).exists())
