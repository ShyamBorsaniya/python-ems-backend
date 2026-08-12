from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company
from department.models import Department
from employee.models import Employee, EmploymentType, EmployeeStatus
from role.models import Role
from project.models import Project, ProjectStatus, ProjectPriority, ProjectMember

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Alpha Corp",
            code="ALPHA",
            email="alpha@example.com"
        )
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering"
        )
        self.project = Project.objects.create(
            company=self.company,
            department=self.department,
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
        self.department = Department.objects.create(
            company=self.company,
            name="Product"
        )
        self.role = Role.objects.create(
            company=self.company,
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

        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            department=self.department,
            employee_code="EMP-001",
            designation="Project Manager",
            joining_date="2024-01-01",
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.ACTIVE
        )

        self.project = Project.objects.create(
            company=self.company,
            department=self.department,
            name="CRM System",
            code="CRM-100",
            status=ProjectStatus.PLANNED,
            priority=ProjectPriority.MEDIUM,
            project_manager=self.employee,
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
            "department": self.department.id,
            "name": "Mobile App",
            "code": "MAP-200",
            "description": "Cross-platform mobile application",
            "status": "ACTIVE",
            "priority": "HIGH",
            "project_manager": self.employee.id,
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
            "department": self.department.id,
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
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering"
        )
        self.role = Role.objects.create(
            company=self.company,
            name="Lead"
        )
        self.user = User.objects.create_user(
            username="memberuser",
            password="password123",
            email="muser@example.com",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)

        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            department=self.department,
            employee_code="EMP-002",
            designation="Backend Developer",
            joining_date="2024-01-01",
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.ACTIVE
        )

        self.project = Project.objects.create(
            company=self.company,
            department=self.department,
            name="E-Commerce Project",
            code="ECM-100",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH
        )

        self.member = ProjectMember.objects.create(
            project=self.project,
            employee=self.employee,
            role="Backend Developer",
            joined_at="2024-02-01"
        )

        self.members_list_create_url = reverse("project-member-list-create")
        self.member_detail_url = reverse("project-member-detail", kwargs={"pk": self.member.pk})

    def test_list_project_members(self):
        response = self.client.get(self.members_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["role"], "Backend Developer")

    def test_create_project_member(self):
        payload = {
            "project": self.project.id,
            "employee": self.employee.id,
            "role": "QA Engineer",
            "joined_at": "2024-03-01"
        }
        response = self.client.post(self.members_list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["role"], "QA Engineer")

    def test_create_project_member_invalid_dates(self):
        payload = {
            "project": self.project.id,
            "employee": self.employee.id,
            "role": "Frontend Developer",
            "joined_at": "2024-05-01",
            "left_at": "2024-04-01"
        }
        response = self.client.post(self.members_list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("left_at", response.data["errors"])

    def test_retrieve_project_member(self):
        response = self.client.get(self.member_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["role"], "Backend Developer")

    def test_update_project_member(self):
        payload = {
            "project": self.project.id,
            "employee": self.employee.id,
            "role": "Project Manager",
            "joined_at": "2024-02-01",
            "left_at": "2024-12-31"
        }
        response = self.client.put(self.member_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["role"], "Project Manager")

    def test_delete_project_member(self):
        response = self.client.delete(self.member_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ProjectMember.objects.filter(pk=self.member.pk).exists())

