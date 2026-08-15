from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from company.models import User, Company, Module, Permission, PermissionSet, PermissionSetPermission


class PermissionSetApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)
        self.company = Company.objects.create(
            name="Test Company",
            code="TESTCO"
        )
        self.permission_set = PermissionSet.objects.create(
            company=self.company,
            name="Standard Manager Kit",
            display_name="Standard Manager Kit",
            code="ps_std_mgr",
            description="Default manager permissions"
        )
        self.list_create_url = reverse("permission-set-list-create")

    def test_list_permission_sets_paginated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_create_global_default_template(self):
        payload = {
            "name": "HR Administrator Suite",
            "display_name": "HR Administrator Suite",
            "code": "ps_hr_admin",
            "description": "Global HR Admin permissions"
        }
        response = self.client.post(self.list_create_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIsNone(response.data["data"]["company"])
        self.assertEqual(response.data["data"]["code"], "ps_hr_admin")

    def test_create_tenant_permission_set(self):
        payload = {
            "company": self.company.id,
            "name": "Finance Admin Suite",
            "display_name": "Finance Admin Suite",
            "code": "ps_fin_admin",
            "description": "Finance admin permissions for test company"
        }
        response = self.client.post(self.list_create_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["company"]["id"], self.company.id)
        self.assertEqual(response.data["data"]["code"], "ps_fin_admin")

    def test_unique_constraint_company_code(self):
        payload = {
            "company": self.company.id,
            "name": "Duplicate Code Kit",
            "display_name": "Duplicate Code Kit",
            "code": "ps_std_mgr",
        }
        response = self.client.post(self.list_create_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data["errors"])

    def test_get_permission_set_detail(self):
        detail_url = reverse("permission-set-detail", kwargs={"pk": self.permission_set.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["code"], "ps_std_mgr")

    def test_update_permission_set(self):
        detail_url = reverse("permission-set-detail", kwargs={"pk": self.permission_set.id})
        payload = {
            "company": self.company.id,
            "name": "Updated Manager Kit",
            "display_name": "Updated Manager Kit",
            "code": "ps_std_mgr",
            "description": "Updated description"
        }
        response = self.client.put(detail_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Updated Manager Kit")

    def test_partial_update_permission_set(self):
        detail_url = reverse("permission-set-detail", kwargs={"pk": self.permission_set.id})
        payload = {"display_name": "Patched Manager Kit"}
        response = self.client.patch(detail_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["display_name"], "Patched Manager Kit")

    def test_delete_permission_set(self):
        detail_url = reverse("permission-set-detail", kwargs={"pk": self.permission_set.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PermissionSet.objects.filter(pk=self.permission_set.id).exists())

    def test_filter_permission_sets(self):
        # Create a global permission set (company is null)
        global_ps = PermissionSet.objects.create(
            company=None,
            name="Global System Kit",
            display_name="Global System Kit",
            code="ps_global_sys",
            description="Global system permissions"
        )

        # Filter by search
        response = self.client.get(f"{self.list_create_url}?search=Manager")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)

        # Filter by company
        response = self.client.get(f"{self.list_create_url}?company={self.company.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["id"], self.permission_set.id)

        # Filter by company (empty string - should ignore company filter and return both)
        response = self.client.get(f"{self.list_create_url}?company=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)

        # Filter by company (null)
        response = self.client.get(f"{self.list_create_url}?company=null")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["id"], global_ps.id)

        # Filter by company (none)
        response = self.client.get(f"{self.list_create_url}?company=none")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["id"], global_ps.id)

        # Filter by code
        response = self.client.get(f"{self.list_create_url}?code=ps_std_mgr")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)


class PermissionSetPermissionApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)
        self.company = Company.objects.create(name="Test Company", code="TESTCO")
        self.module = Module.objects.create(
            company=self.company,
            name="Employee Module",
            display_name="Employee Module",
            code="emp_mod"
        )
        self.permission = Permission.objects.create(
            company=self.company,
            module=self.module,
            name="employee.view",
            display_name="View Employee",
            code="emp:view",
            action="view"
        )
        self.permission_set = PermissionSet.objects.create(
            company=self.company,
            name="HR Kit",
            display_name="HR Kit",
            code="ps_hr"
        )
        self.ps_permission = PermissionSetPermission.objects.create(
            permission_set=self.permission_set,
            permission=self.permission
        )
        self.list_create_url = reverse("permission-set-permission-list-create")

    def test_list_permission_set_permissions(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_create_permission_set_permission(self):
        new_perm = Permission.objects.create(
            company=self.company,
            module=self.module,
            name="employee.edit",
            display_name="Edit Employee",
            code="emp:edit",
            action="edit"
        )
        payload = {
            "permission_set": self.permission_set.id,
            "permission": new_perm.id
        }
        response = self.client.post(self.list_create_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["permission"]["id"], new_perm.id)

    def test_duplicate_permission_set_permission(self):
        payload = {
            "permission_set": self.permission_set.id,
            "permission": self.permission.id
        }
        response = self.client.post(self.list_create_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("permission", response.data["errors"])

    def test_get_permission_set_permission_detail(self):
        detail_url = reverse("permission-set-permission-detail", kwargs={"pk": self.ps_permission.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], self.ps_permission.id)

    def test_delete_permission_set_permission(self):
        detail_url = reverse("permission-set-permission-detail", kwargs={"pk": self.ps_permission.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PermissionSetPermission.objects.filter(pk=self.ps_permission.id).exists())

    def test_filter_permission_set_permissions(self):
        response = self.client.get(f"{self.list_create_url}?permission_set={self.permission_set.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)

        response = self.client.get(f"{self.list_create_url}?search=HR Kit")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
