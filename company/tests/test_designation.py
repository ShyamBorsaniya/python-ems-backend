from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from company.models import Company, Department, Designation, DesignationPermissionSet, Role, PermissionSet

User = get_user_model()


class DesignationModelTest(TestCase):
    def test_designation_fields_are_present(self):
        company = Company.objects.create(name='Acme', code='ACME')
        department = Department.objects.create(company=company, name='Engineering', code='ENG')
        designation = Designation.objects.create(
            company=company,
            department=department,
            name='Senior Developer',
            code='SD',
            description='Senior engineering role',
            is_active=True,
        )

        self.assertEqual(designation.company, company)
        self.assertEqual(designation.department, department)
        self.assertEqual(designation.name, 'Senior Developer')
        self.assertEqual(designation.code, 'SD')
        self.assertTrue(designation.is_active)


class DesignationPermissionSetAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme Inc", code="ACME")
        self.role = Role.objects.create(name="Admin Role")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="user@example.com",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.department = Department.objects.create(company=self.company, name="Engineering", code="ENG")
        self.designation = Designation.objects.create(company=self.company, department=self.department, name="Lead Dev", code="LEAD")
        self.permission_set = PermissionSet.objects.create(company=self.company, name="Lead Kit", code="ps_lead")
        self.list_create_url = reverse("designation-permission-set-list-create")

    def test_assign_permission_set_to_designation(self):
        payload = {
            "designation": self.designation.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_duplicate_designation_permission_set(self):
        DesignationPermissionSet.objects.create(designation=self.designation, permission_set=self.permission_set)
        payload = {
            "designation": self.designation.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_and_detail_designation_permission_set(self):
        dps = DesignationPermissionSet.objects.create(designation=self.designation, permission_set=self.permission_set)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)

        detail_url = reverse("designation-permission-set-detail", kwargs={"pk": dps.pk})
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(DesignationPermissionSet.objects.filter(pk=dps.pk).exists())
