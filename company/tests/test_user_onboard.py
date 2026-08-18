from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from company.models import User, Employee, Company, Role, Department, Designation, UserStatus, EmploymentType, EmploymentStatus, Gender
from django.utils import timezone


class UserOnboardAPITests(APITestCase):

    def setUp(self):
        # Create company
        self.company = Company.objects.create(
            name="Test Corp",
            code="TC",
            email="info@testcorp.com"
        )
        # Create department & designation
        self.department = Department.objects.create(company=self.company, name="Engineering", code="ENG")
        self.designation = Designation.objects.create(company=self.company, department=self.department, name="Software Developer", code="SDE")

        # Create roles
        self.role = Role.objects.create(
            name="Engineer",
            display_name="Engineers systems"
        )

        # Create admin/superuser user to perform actions (or a user with user_management permissions)
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@testcorp.com",
            password="Password123!",
            company=self.company,
            role=self.role
        )

        self.onboard_url = reverse("user-onboard")
        self.onboard_detail_url_name = "user-onboard-detail"

        # Valid payload data
        self.onboard_payload = {
            "username": "onboard_user",
            "email": "onboard@testcorp.com",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "9876543210",
            "is_active": False,
            "company": self.company.id,
            "role": self.role.id,
            "status": "approve",
            # Nested Employee fields
            "employee_details": {
                "code": "EMP-TC-001",
                "department": self.department.id,
                "designation": self.designation.id,
                "employment_type": "full_time",
                "employment_status": "active",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "address": "123 Test St",
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "1234567890"
            }
        }

    def test_onboard_unauthenticated_fails(self):
        response = self.client.post(self.onboard_url, self.onboard_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_onboard_user_and_employee_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.onboard_url, self.onboard_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        # Verify response structure
        data = response.data["data"]
        self.assertEqual(data["username"], "onboard_user")
        self.assertEqual(data["email"], "onboard@testcorp.com")
        self.assertFalse(data["is_active"])

        # Verify nested employee details
        emp_details = data["employee_details"]
        self.assertEqual(emp_details["code"], "EMP-TC-001")
        self.assertEqual(emp_details["department"], self.department.id)
        self.assertEqual(emp_details["designation"], self.designation.id)
        self.assertEqual(emp_details["employment_type"], "full_time")
        self.assertEqual(emp_details["gender"], "male")
        self.assertEqual(emp_details["emergency_contact_name"], "Jane Doe")

        # Verify DB records
        user = User.objects.get(username="onboard_user")
        self.assertEqual(user.email, "onboard@testcorp.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.phone, "9876543210")
        self.assertFalse(user.is_active)

        employee = Employee.objects.get(user=user)
        self.assertEqual(employee.code, "EMP-TC-001")
        self.assertEqual(employee.company, self.company)
        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.designation, self.designation)
        self.assertEqual(str(employee.date_of_birth), "1990-01-01")
        self.assertEqual(employee.address, "123 Test St")
        self.assertEqual(employee.emergency_contact_phone, "1234567890")

    def test_onboard_auto_generates_code(self):
        self.client.force_authenticate(user=self.admin_user)
        import copy
        payload = copy.deepcopy(self.onboard_payload)
        payload["username"] = "auto_code_user"
        payload["email"] = "autocode@testcorp.com"
        del payload["employee_details"]["code"]  # Should trigger auto generation

        response = self.client.post(self.onboard_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        # Check DB
        user = User.objects.get(username="auto_code_user")
        employee = Employee.objects.get(user=user)
        self.assertTrue(employee.code.startswith(f"EMP-TC-{timezone.now().year}-"))
        self.assertEqual(len(employee.code), len(f"EMP-TC-{timezone.now().year}-") + 4)

    def test_onboard_with_invalid_dept_or_desig_fails(self):
        self.client.force_authenticate(user=self.admin_user)

        # Create another company and its department
        other_company = Company.objects.create(name="Other Corp", code="OC")
        other_dept = Department.objects.create(company=other_company, name="HR", code="HR")

        import copy
        payload = copy.deepcopy(self.onboard_payload)
        payload["username"] = "invalid_dept_user"
        payload["email"] = "invaliddept@testcorp.com"
        payload["employee_details"]["department"] = other_dept.id # Dept from other company

        response = self.client.post(self.onboard_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        # Validation error will be nested under employee_details
        self.assertIn("employee_details", response.data["errors"])
        self.assertIn("department", response.data["errors"]["employee_details"])

    def test_onboard_with_duplicate_employee_code_fails(self):
        self.client.force_authenticate(user=self.admin_user)

        # Onboard first user
        self.client.post(self.onboard_url, self.onboard_payload, format="json")

        # Attempt to onboard second user with same code
        import copy
        payload = copy.deepcopy(self.onboard_payload)
        payload["username"] = "another_user"
        payload["email"] = "another@testcorp.com"
        # code is same: EMP-TC-001

        response = self.client.post(self.onboard_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("employee_details", response.data["errors"])
        self.assertIn("code", response.data["errors"]["employee_details"])

    def test_patch_onboard_user_and_employee_success(self):
        self.client.force_authenticate(user=self.admin_user)

        # First onboard a user
        post_response = self.client.post(self.onboard_url, self.onboard_payload, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        user_id = post_response.data["data"]["id"]

        # Now patch details
        patch_payload = {
            "first_name": "Jonathan",
            "last_name": "Smith",
            "phone": "5555555555",
            "is_active": True,
            "employee_details": {
                "employment_type": "contract",
                "address": "456 New Rd",
                "emergency_contact_name": "Jane Smith"
            }
        }

        detail_url = reverse(self.onboard_detail_url_name, kwargs={"pk": user_id})
        response = self.client.patch(detail_url, patch_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verify response
        data = response.data["data"]
        self.assertEqual(data["first_name"], "Jonathan")
        self.assertEqual(data["last_name"], "Smith")
        self.assertEqual(data["phone"], "5555555555")
        self.assertTrue(data["is_active"])

        emp_details = data["employee_details"]
        self.assertEqual(emp_details["employment_type"], "contract")
        self.assertEqual(emp_details["address"], "456 New Rd")
        self.assertEqual(emp_details["emergency_contact_name"], "Jane Smith")

        # Verify DB
        user = User.objects.get(pk=user_id)
        self.assertEqual(user.first_name, "Jonathan")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.phone, "5555555555")
        self.assertTrue(user.is_active)

        employee = Employee.objects.get(user=user)
        self.assertEqual(employee.employment_type, "contract")
        self.assertEqual(employee.address, "456 New Rd")
        self.assertEqual(employee.emergency_contact_name, "Jane Smith")
