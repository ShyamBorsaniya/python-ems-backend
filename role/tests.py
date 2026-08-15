from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from user.models import User
from company.models import Company
from module.models import Module
from role.models import Role, RolePermission, RolePermissionSet
from permission.models import Permission
from permission_set.models import PermissionSet


class RoleApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Tech Corp",
            code="TECH01",
            email="info@techcorp.com"
        )
        self.role = Role.objects.create(
            name="Admin",
            display_name="Administrator role"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="user@techcorp.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("role-list-create")

    def test_list_roles_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_create_role_unauthenticated(self):
        unauthenticated_client = APIClient()
        payload = {
            "name": "Quality Analyst",
            "display_name": "Tests software"
        }
        response = unauthenticated_client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_roles_paginated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertEqual(response.data["data"]["pagination"]["page"], 1)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 10)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_list_roles_pagination_multiple_pages(self):
        # Create 12 total roles (1 exists + 11 new)
        for i in range(11):
            Role.objects.create(
                name=f"Role {i}",
                display_name=f"Description {i}"
            )

        # Page 1
        page1 = self.client.get(self.list_create_url)
        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page1.data["data"]["results"]), 10)
        self.assertEqual(page1.data["data"]["pagination"]["page"], 1)
        self.assertEqual(page1.data["data"]["pagination"]["total_items"], 12)
        self.assertEqual(page1.data["data"]["pagination"]["total_pages"], 2)
        self.assertEqual(page1.data["data"]["pagination"]["next_page"], 2)
        self.assertIsNone(page1.data["data"]["pagination"]["previous_page"])

        # Page 2
        page2 = self.client.get(f"{self.list_create_url}?page=2")
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data["data"]["results"]), 2)
        self.assertEqual(page2.data["data"]["pagination"]["page"], 2)
        self.assertIsNone(page2.data["data"]["pagination"]["next_page"])
        self.assertEqual(page2.data["data"]["pagination"]["previous_page"], 1)

    def test_list_roles_custom_page_size(self):
        for i in range(4):
            Role.objects.create(
                name=f"Custom Role {i}"
            )
        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)
        self.assertEqual(response.data["data"]["pagination"]["total_pages"], 3)

    def test_list_roles_filter_by_search(self):
        Role.objects.create(
            name="Developer",
            display_name="Writes code"
        )
        Role.objects.create(
            name="External Auditor",
            display_name="Audit company"
        )

        # Search filter
        res_search = self.client.get(f"{self.list_create_url}?search=Developer")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_search.data["data"]["results"]), 1)
        self.assertEqual(res_search.data["data"]["results"][0]["name"], "Developer")

    def test_create_role(self):
        payload = {
            "name": "Quality Analyst",
            "display_name": "Tests software"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["name"], "Quality Analyst")
        self.assertEqual(response.data["data"]["display_name"], "Tests software")

    def test_role_name_uniqueness(self):
        payload = {
            "name": "Admin",
            "display_name": "Another Admin"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_role_detail_update_delete(self):
        detail_url = reverse("role-detail", kwargs={"pk": self.role.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["name"], "Admin")

        # PUT update
        update_payload = {
            "name": "Super Admin",
            "display_name": "Updated description"
        }
        put_res = self.client.put(detail_url, update_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["name"], "Super Admin")
        self.assertEqual(put_res.data["data"]["display_name"], "Updated description")

        # PATCH update name
        patch_res = self.client.patch(detail_url, {"name": "Chief Executive"}, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["data"]["name"], "Chief Executive")

        # DELETE assigned role (should fail with 400 due to ProtectedError)
        del_assigned_res = self.client.delete(detail_url)
        self.assertEqual(del_assigned_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(del_assigned_res.data["success"])

        # DELETE unassigned role (should succeed with 200 OK)
        unassigned_role = Role.objects.create(name="Unassigned Role")
        unassigned_url = reverse("role-detail", kwargs={"pk": unassigned_role.pk})
        del_unassigned_res = self.client.delete(unassigned_url)
        self.assertEqual(del_unassigned_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Role.objects.filter(pk=unassigned_role.pk).exists())


class RolePermissionApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Tech Corp",
            code="TECH01",
            email="info@techcorp.com"
        )
        self.role = Role.objects.create(
            name="HR Manager",
            display_name="HR Manager role"
        )
        self.module = Module.objects.create(
            company=self.company,
            name="Company Module",
            display_name="Company Module",
            code="company_mod"
        )
        self.permission1 = Permission.objects.create(
            module=self.module,
            name="company.create",
            display_name="Create Company",
            code="company:create",
            action="create",
            description="Create company"
        )
        self.permission2 = Permission.objects.create(
            module=self.module,
            name="company.read",
            display_name="Read Company",
            code="company:read",
            action="read",
            description="Read company"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="user@techcorp.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("role-permission-list-create")

    def test_assign_permission_to_role(self):
        payload = {
            "role": self.role.id,
            "permission": self.permission1.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["role"], self.role.id)
        self.assertEqual(response.data["data"]["permission"], self.permission1.id)
        self.assertEqual(response.data["data"]["role_name"], "HR Manager")
        self.assertEqual(response.data["data"]["permission_name"], "company.create")

    def test_duplicate_permission_assignment(self):
        RolePermission.objects.create(role=self.role, permission=self.permission1)
        payload = {
            "role": self.role.id,
            "permission": self.permission1.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_list_and_filter_role_permissions(self):
        RolePermission.objects.create(role=self.role, permission=self.permission1)
        RolePermission.objects.create(role=self.role, permission=self.permission2)

        # List all
        res = self.client.get(self.list_create_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["data"]["pagination"]["total_items"], 2)

        # Filter by role
        res_role = self.client.get(f"{self.list_create_url}?role={self.role.id}")
        self.assertEqual(res_role.status_code, status.HTTP_200_OK)
        self.assertEqual(res_role.data["data"]["pagination"]["total_items"], 2)

        # Filter by permission
        res_perm = self.client.get(f"{self.list_create_url}?permission={self.permission1.id}")
        self.assertEqual(res_perm.status_code, status.HTTP_200_OK)
        self.assertEqual(res_perm.data["data"]["pagination"]["total_items"], 1)

    def test_role_permission_detail_and_delete(self):
        rp = RolePermission.objects.create(role=self.role, permission=self.permission1)
        detail_url = reverse("role-permission-detail", kwargs={"pk": rp.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["permission_name"], "company.create")

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(RolePermission.objects.filter(pk=rp.pk).exists())


class RolePermissionSetApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(name="Tech Corp", code="TECH01")
        self.role = Role.objects.create(name="HR Manager", display_name="HR Manager")
        self.permission_set = PermissionSet.objects.create(
            company=self.company,
            name="HR Kit",
            display_name="HR Kit",
            code="ps_hr"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="user@techcorp.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse("role-permission-set-list-create")

    def test_assign_permission_set_to_role(self):
        payload = {
            "role": self.role.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["permission_set"]["id"], self.permission_set.id)

    def test_duplicate_permission_set_assignment(self):
        RolePermissionSet.objects.create(role=self.role, permission_set=self.permission_set)
        payload = {
            "role": self.role.id,
            "permission_set": self.permission_set.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_and_filter_role_permission_sets(self):
        RolePermissionSet.objects.create(role=self.role, permission_set=self.permission_set)
        res = self.client.get(self.list_create_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["data"]["pagination"]["total_items"], 1)

        res_filtered = self.client.get(f"{self.list_create_url}?role={self.role.id}")
        self.assertEqual(res_filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_filtered.data["data"]["results"]), 1)

    def test_role_permission_set_detail_and_delete(self):
        rps = RolePermissionSet.objects.create(role=self.role, permission_set=self.permission_set)
        detail_url = reverse("role-permission-set-detail", kwargs={"pk": rps.pk})

        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)

        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(RolePermissionSet.objects.filter(pk=rps.pk).exists())

