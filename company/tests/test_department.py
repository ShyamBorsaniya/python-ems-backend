from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company, Role, Department, DepartmentPermissionSet, PermissionSet, Module, Permission

User = get_user_model()


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="TechCorp",
            code="TC001"
        )
        self.role = Role.objects.create(
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
            name="Admin Role"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="user@example.com",
            role=self.role,
            company=self.company,
            is_superuser=True
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
            "code": "HR",
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
            "code": "HR",
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


class DepartmentPermissionSetAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme Inc", code="ACME")
        self.role = Role.objects.create(name="Admin Role")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="user@example.com",
            role=self.role,
            company=self.company,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.department = Department.objects.create(company=self.company, name="Engineering", code="ENG")
        self.permission_set = PermissionSet.objects.create(company=self.company, name="Eng Kit", code="ps_eng")
        self.list_create_url = reverse("department-permission-set-list-create")

    def test_assign_permission_set_to_department(self):
        payload = {
            "department": self.department.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_duplicate_department_permission_set(self):
        DepartmentPermissionSet.objects.create(department=self.department, permission_set=self.permission_set)
        payload = {
            "department": self.department.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_and_detail_department_permission_set(self):
        dps = DepartmentPermissionSet.objects.create(department=self.department, permission_set=self.permission_set)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)

        detail_url = reverse("department-permission-set-detail", kwargs={"pk": dps.pk})
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(DepartmentPermissionSet.objects.filter(pk=dps.pk).exists())


class DepartmentAuthorizationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme Auth Dept", code="ADEPTAUTH")
        self.role = Role.objects.create(name="Authorized Role")
        self.user = User.objects.create_user(
            username="authuserdept",
            password="testpassword123",
            email="authuserdept@example.com",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.department_url = reverse("department-list-create")

    def test_list_departments_without_permission_denied(self):
        response = self.client.get(self.department_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_departments_with_permission_allowed(self):
        # Create department_management module and view permission, assign to user's role
        from company.models import PermissionSetPermission, RolePermissionSet
        module = Module.objects.create(company=self.company, name="Department Module", code="department_management")
        permission = Permission.objects.create(
            company=self.company,
            module=module,
            name="department.view",
            code="department:view",
            action="view"
        )
        perm_set = PermissionSet.objects.create(company=self.company, name="Department Reader", code="dept_reader")
        PermissionSetPermission.objects.create(permission_set=perm_set, permission=permission)
        RolePermissionSet.objects.create(role=self.role, permission_set=perm_set)

        response = self.client.get(self.department_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DepartmentDesignationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(
            name="Test Corp",
            code="TEST"
        )
        self.role = Role.objects.create(name="Admin Role")
        self.user = User.objects.create_user(
            username="testadmin",
            password="testpassword123",
            email="admin@test.com",
            role=self.role,
            company=self.company,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        
        self.dept1 = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG"
        )
        self.dept2 = Department.objects.create(
            company=self.company,
            name="HR",
            code="HR"
        )
        
        from company.models import Designation
        self.des1 = Designation.objects.create(
            company=self.company,
            department=self.dept1,
            name="Software Engineer",
            code="SE"
        )
        self.des2 = Designation.objects.create(
            company=self.company,
            department=self.dept1,
            name="Senior Engineer",
            code="SSE",
            is_active=False
        )
        
        self.url = reverse("department-designation-list")

    def test_get_department_designations_nested(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        
        results = response.data["data"]
        self.assertEqual(len(results), 2)
        
        eng_data = next(d for d in results if d["name"] == "Engineering")
        self.assertEqual(len(eng_data["designations"]), 2)
        des_names = [d["name"] for d in eng_data["designations"]]
        self.assertIn("Software Engineer", des_names)
        self.assertIn("Senior Engineer", des_names)

    def test_get_department_designations_flat(self):
        response = self.client.get(f"{self.url}?format=flat")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]
        
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results["Engineering"]), 2)
        self.assertIn("Software Engineer", results["Engineering"])
        self.assertEqual(results["HR"], [])

    def test_get_department_designations_grouped(self):
        response = self.client.get(f"{self.url}?format=grouped")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]
        
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results["Engineering"]), 2)
        self.assertEqual(results["Engineering"][0]["name"], "Software Engineer")
        self.assertEqual(results["Engineering"][0]["code"], "SE")

    def test_get_department_designations_is_active(self):
        response = self.client.get(f"{self.url}?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]
        
        eng_data = next(d for d in results if d["name"] == "Engineering")
        self.assertEqual(len(eng_data["designations"]), 1)
        self.assertEqual(eng_data["designations"][0]["name"], "Software Engineer")


