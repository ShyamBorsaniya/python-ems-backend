from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from company.models import Company
from department.models import Department
from role.models import Role
from .models import Employee, EmploymentType, EmployeeStatus


class EmployeeApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Tech Enterprise",
            code="TE001",
            email="contact@techenterprise.com"
        )
        self.role = Role.objects.create(
            company=self.company,
            name="Admin Role"
        )
        self.user = User.objects.create_user(
            username="emp_admin",
            email="admin@techenterprise.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG"
        )
        self.employee = Employee.objects.create(
            company=self.company,
            department=self.department,
            user=self.user,
            employee_code="EMP001",
            designation="Senior Software Engineer",
            joining_date=date(2025, 1, 15),
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.ACTIVE
        )
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("employee-list-create")

    def test_list_employees_paginated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["pagination"]["page"], 1)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 10)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_list_employees_pagination_multiple_pages(self):
        # Create 11 more employees
        for i in range(11):
            Employee.objects.create(
                company=self.company,
                department=self.department,
                employee_code=f"EMP{i+2:03d}",
                designation=f"Developer {i}",
                joining_date=date(2025, 1, 15)
            )

        page1 = self.client.get(self.list_create_url)
        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page1.data["data"]["results"]), 10)
        self.assertEqual(page1.data["data"]["pagination"]["page"], 1)
        self.assertEqual(page1.data["data"]["pagination"]["total_items"], 12)
        self.assertEqual(page1.data["data"]["pagination"]["total_pages"], 2)
        self.assertEqual(page1.data["data"]["pagination"]["next_page"], 2)

        page2 = self.client.get(f"{self.list_create_url}?page=2")
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data["data"]["results"]), 2)
        self.assertEqual(page2.data["data"]["pagination"]["page"], 2)
        self.assertIsNone(page2.data["data"]["pagination"]["next_page"])

    def test_list_employees_custom_page_size(self):
        for i in range(4):
            Employee.objects.create(
                company=self.company,
                employee_code=f"EMPCUST{i:03d}",
                designation=f"Role {i}",
                joining_date=date(2025, 1, 15)
            )

        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)
        self.assertEqual(response.data["data"]["pagination"]["total_pages"], 3)

    def test_list_employees_filtering_with_pagination(self):
        Employee.objects.create(
            company=self.company,
            employee_code="EMP_CONTRACT",
            designation="Contractor",
            joining_date=date(2025, 2, 1),
            employment_type=EmploymentType.CONTRACT,
            status=EmployeeStatus.INACTIVE
        )

        res_type = self.client.get(f"{self.list_create_url}?employment_type=CONTRACT")
        self.assertEqual(res_type.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_type.data["data"]["results"]), 1)
        self.assertEqual(res_type.data["data"]["results"][0]["employee_code"], "EMP_CONTRACT")

        res_status = self.client.get(f"{self.list_create_url}?status=INACTIVE")
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)
        self.assertEqual(res_status.data["data"]["pagination"]["total_items"], 1)

    def test_create_employee(self):
        payload = {
            "company": self.company.id,
            "department": self.department.id,
            "employee_code": "EMPNEW01",
            "designation": "QA Engineer",
            "joining_date": "2025-03-01",
            "employment_type": "FULL_TIME",
            "status": "ACTIVE"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["employee_code"], "EMPNEW01")

    def test_retrieve_update_delete_employee(self):
        detail_url = reverse("employee-detail", kwargs={"pk": self.employee.pk})

        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["employee_code"], "EMP001")

        update_payload = {
            "company": self.company.id,
            "employee_code": "EMP001",
            "designation": "Lead Engineer",
            "joining_date": "2025-01-15"
        }
        put_res = self.client.put(detail_url, update_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["designation"], "Lead Engineer")

        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())
