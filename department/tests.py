from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company
from role.models import Role
from employee.models import Employee
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
            code="ENG",
            description="Software and Hardware engineering",
            is_active=True
        )

    def test_department_creation(self):
        self.assertEqual(self.department.name, "Engineering")
        self.assertEqual(self.department.code, "ENG")
        self.assertEqual(self.department.company, self.company)
        self.assertTrue(self.department.is_active)
        self.assertEqual(str(self.department), "Engineering (ENG)")


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
            code="HR",
            description="HR Department"
        )
        self.list_create_url = reverse("department-list-create")
        self.detail_url = reverse("department-detail", kwargs={"pk": self.department.pk})

    def test_list_departments(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["pagination"]["page"], 1)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 10)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_list_departments_pagination_multiple_pages(self):
        for i in range(11):
            Department.objects.create(
                company=self.company,
                name=f"Department {i}",
                code=f"D{i}"
            )
        page1 = self.client.get(self.list_create_url)
        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page1.data["data"]["results"]), 10)
        self.assertEqual(page1.data["data"]["pagination"]["total_items"], 12)
        self.assertEqual(page1.data["data"]["pagination"]["total_pages"], 2)
        self.assertEqual(page1.data["data"]["pagination"]["next_page"], 2)

        page2 = self.client.get(f"{self.list_create_url}?page=2")
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data["data"]["results"]), 2)
        self.assertEqual(page2.data["data"]["pagination"]["page"], 2)
        self.assertIsNone(page2.data["data"]["pagination"]["next_page"])

    def test_list_departments_custom_page_size(self):
        for i in range(4):
            Department.objects.create(
                company=self.company,
                name=f"Custom Dept {i}",
                code=f"CD{i}"
            )
        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)
        self.assertEqual(response.data["data"]["pagination"]["total_pages"], 3)

    def test_create_department_success(self):
        payload = {
            "company": self.company.id,
            "name": "Finance",
            "code": "FIN",
            "description": "Finance and Accounting",
            "is_active": True
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Finance")
        self.assertEqual(response.data["data"]["code"], "FIN")

    def test_create_department_duplicate_code_same_company_fails(self):
        payload = {
            "company": self.company.id,
            "name": "Another HR",
            "code": "HR",  # duplicate code in same company
            "description": "Duplicate code test"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_create_department_same_code_different_company_success(self):
        other_company = Company.objects.create(name="OtherCorp", code="OTHER")
        payload = {
            "company": other_company.id,
            "name": "Human Resources",
            "code": "HR",  # same code as self.company, but different company
            "description": "HR in OtherCorp"
        }
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["code"], "HR")

    def test_search_department_by_code(self):
        response = self.client.get(f"{self.list_create_url}?search=HR")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["code"], "HR")

    def test_retrieve_department(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Human Resources")
        self.assertEqual(response.data["data"]["code"], "HR")

    def test_update_department(self):
        payload = {
            "company": self.company.id,
            "name": "People Operations",
            "code": "PO",
            "description": "Updated HR Dept",
            "is_active": True
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "People Operations")
        self.assertEqual(response.data["data"]["code"], "PO")

    def test_partial_update_department(self):
        payload = {
            "name": "Global HR",
            "code": "GHR"
        }
        response = self.client.patch(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Global HR")
        self.assertEqual(response.data["data"]["code"], "GHR")

    def test_delete_department(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Department.objects.filter(pk=self.department.pk).exists())

    def test_department_employee_count(self):
        import datetime
        Employee.objects.create(
            company=self.company,
            department=self.department,
            employee_code="EMP_TEST_1",
            designation="Dev",
            joining_date=datetime.date(2025, 1, 1)
        )
        Employee.objects.create(
            company=self.company,
            department=self.department,
            employee_code="EMP_TEST_2",
            designation="QA",
            joining_date=datetime.date(2025, 1, 1)
        )
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["employee_count"], 2)
