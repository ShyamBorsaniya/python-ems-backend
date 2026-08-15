from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from company.models import User, Company, Department, Designation, Employee, EmploymentType, EmploymentStatus, Gender


class EmployeeApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Acme Corp",
            code="ACME01",
            email="hr@acme.com"
        )
        self.other_company = Company.objects.create(
            name="Global Inc",
            code="GLOB01",
            email="hr@global.com"
        )

        self.department = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG01"
        )
        self.other_department = Department.objects.create(
            company=self.other_company,
            name="Finance",
            code="FIN01"
        )

        self.designation = Designation.objects.create(
            company=self.company,
            name="Software Engineer",
            code="SE01"
        )

        self.user = User.objects.create_user(
            username="john_doe",
            email="john@acme.com",
            password="Password123!",
            first_name="John",
            last_name="Doe"
        )
        self.user2 = User.objects.create_user(
            username="jane_smith",
            email="jane@acme.com",
            password="Password123!",
            first_name="Jane",
            last_name="Smith"
        )

        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("employee-list-create")

        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            code="EMP001",
            department=self.department,
            designation=self.designation,
            joining_date="2024-01-15",
            employment_type=EmploymentType.FULL_TIME,
            employment_status=EmploymentStatus.ACTIVE,
            date_of_birth="1995-05-20",
            gender=Gender.MALE,
            address="123 Main St, Tech City",
            emergency_contact_name="Mary Doe",
            emergency_contact_phone="+1234567890"
        )

    def test_list_employees_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_employees_authenticated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)
        self.assertEqual(response.data["data"]["results"][0]["code"], "EMP001")
        self.assertEqual(response.data["data"]["results"][0]["user_username"], "john_doe")

    def test_create_employee_success(self):
        payload = {
            "user": self.user2.id,
            "company": self.company.id,
            "code": "EMP002",
            "department": self.department.id,
            "designation": self.designation.id,
            "joining_date": "2024-02-01",
            "employment_type": EmploymentType.CONTRACT,
            "employment_status": EmploymentStatus.ACTIVE,
            "gender": Gender.FEMALE,
            "address": "456 Side St",
            "emergency_contact_name": "Bob Smith",
            "emergency_contact_phone": "+9876543210"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["code"], "EMP002")
        self.assertEqual(response.data["data"]["user_username"], "jane_smith")

    def test_create_employee_duplicate_code_same_company(self):
        payload = {
            "user": self.user2.id,
            "company": self.company.id,
            "code": "EMP001",  # Same code as self.employee
            "joining_date": "2024-02-01"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertTrue("code" in response.data["errors"] or "non_field_errors" in response.data["errors"])

    def test_create_employee_duplicate_user(self):
        payload = {
            "user": self.user.id,  # Already has employee profile
            "company": self.company.id,
            "code": "EMP999",
            "joining_date": "2024-02-01"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("user", response.data["errors"])

    def test_create_employee_mismatched_department_company(self):
        payload = {
            "user": self.user2.id,
            "company": self.company.id,
            "code": "EMP003",
            "department": self.other_department.id,  # Belongs to other_company
            "joining_date": "2024-02-01"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("department", response.data["errors"])

    def test_search_and_filtering(self):
        # Search by code
        res_code = self.client.get(f"{self.list_create_url}?search=EMP001")
        self.assertEqual(res_code.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_code.data["data"]["results"]), 1)

        # Search by user first name
        res_name = self.client.get(f"{self.list_create_url}?search=John")
        self.assertEqual(res_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_name.data["data"]["results"]), 1)

        # Filter by employment_type
        res_type = self.client.get(f"{self.list_create_url}?employment_type=full_time")
        self.assertEqual(res_type.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_type.data["data"]["results"]), 1)

        # Filter by status
        res_status = self.client.get(f"{self.list_create_url}?employment_status=resigned")
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_status.data["data"]["results"]), 0)

    def test_employee_detail_update_delete(self):
        detail_url = reverse("employee-detail", kwargs={"pk": self.employee.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["code"], "EMP001")

        # PATCH update employment status
        patch_res = self.client.patch(detail_url, {"employment_status": EmploymentStatus.ON_LEAVE}, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["data"]["employment_status"], EmploymentStatus.ON_LEAVE)

        # PUT update full object
        put_payload = {
            "user": self.user.id,
            "company": self.company.id,
            "code": "EMP001_UPDATED",
            "department": self.department.id,
            "designation": self.designation.id,
            "joining_date": "2024-01-15",
            "employment_type": EmploymentType.FULL_TIME,
            "employment_status": EmploymentStatus.ACTIVE,
            "date_of_birth": "1995-05-20",
            "gender": Gender.MALE,
            "address": "789 New Address",
            "emergency_contact_name": "Mary Doe",
            "emergency_contact_phone": "+1234567890"
        }
        put_res = self.client.put(detail_url, put_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["code"], "EMP001_UPDATED")
        self.assertEqual(put_res.data["data"]["address"], "789 New Address")

        # DELETE employee
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())
