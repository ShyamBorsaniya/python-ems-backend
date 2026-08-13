from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from user.models import User
from company.models import Company
from role.models import Role, RolePermission
from permission.models import Permission


class RoleApiTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Tech Corp",
            code="TECH01",
            email="info@techcorp.com"
        )
        self.other_company = Company.objects.create(
            name="Other Corp",
            code="OTHER01",
            email="info@othercorp.com"
        )
        self.role = Role.objects.create(
            company=self.company,
            name="Admin",
            description="Administrator role"
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

    def test_list_roles_unauthenticated_filter_by_company(self):
        unauthenticated_client = APIClient()
        Role.objects.create(
            company=self.other_company,
            name="Other Company Role"
        )
        response = unauthenticated_client.get(f"{self.list_create_url}?company={self.other_company.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)
        self.assertEqual(response.data["data"]["results"][0]["name"], "Other Company Role")

    def test_create_role_unauthenticated(self):
        unauthenticated_client = APIClient()
        payload = {
            "name": "Quality Analyst",
            "description": "Tests software",
            "company": self.company.id
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
                company=self.company,
                name=f"Role {i}",
                description=f"Description {i}"
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
                company=self.company,
                name=f"Custom Role {i}"
            )
        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)
        self.assertEqual(response.data["data"]["pagination"]["total_pages"], 3)

    def test_list_roles_filter_by_search_and_company(self):
        Role.objects.create(
            company=self.company,
            name="Developer",
            description="Writes code"
        )
        Role.objects.create(
            company=self.other_company,
            name="External Auditor",
            description="Audit company"
        )

        # Search filter (user belongs to self.company, so only self.company roles are included)
        res_search = self.client.get(f"{self.list_create_url}?search=Developer")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_search.data["data"]["results"]), 1)
        self.assertEqual(res_search.data["data"]["results"][0]["name"], "Developer")

        # Company filter (user already scoped to self.company)
        res_company = self.client.get(f"{self.list_create_url}?company={self.company.id}")
        self.assertEqual(res_company.status_code, status.HTTP_200_OK)
        self.assertEqual(res_company.data["data"]["pagination"]["total_items"], 2)

    def test_list_roles_filters_automatically_by_user_company(self):
        Role.objects.create(
            company=self.other_company,
            name="Other Company Role",
            description="Role in another company"
        )
        # self.user belongs to self.company, so other company role should not be listed
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        role_ids = [r["id"] for r in response.data["data"]["results"]]
        self.assertIn(self.role.id, role_ids)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_list_roles_user_without_company(self):
        user_no_company = User.objects.create_user(
            username="nocompanyuser",
            email="nocompany@example.com",
            password="Password123!",
            company=None
        )
        Role.objects.create(
            company=self.other_company,
            name="Other Company Role"
        )
        self.client.force_authenticate(user=user_no_company)

        # Should list all roles from all companies
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 2)

        # Filtering by company_id query param
        response_param = self.client.get(f"{self.list_create_url}?company={self.other_company.id}")
        self.assertEqual(response_param.status_code, status.HTTP_200_OK)
        self.assertEqual(response_param.data["data"]["pagination"]["total_items"], 1)
        self.assertEqual(response_param.data["data"]["results"][0]["name"], "Other Company Role")

    def test_create_role(self):
        payload = {
            "name": "Quality Analyst",
            "description": "Tests software",
            "company": self.company.id
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["name"], "Quality Analyst")
        self.assertEqual(response.data["data"]["code"], "QUALITY_ANALYST")

    def test_auto_generate_code_and_uniqueness(self):
        role1 = Role.objects.create(name="Team Lead", company=self.company)
        self.assertEqual(role1.code, "TEAM_LEAD")

        role2 = Role.objects.create(name="Team Lead", company=self.other_company)
        self.assertEqual(role2.code, "TEAM_LEAD_1")

        role3 = Role.objects.create(name="Team Lead", company=self.company)
        self.assertEqual(role3.code, "TEAM_LEAD_2")

    def test_system_role_creation_without_company(self):
        system_role = Role.objects.create(
            name="Super Admin",
            is_system_role=True,
            company=None
        )
        self.assertEqual(system_role.code, "SUPER_ADMIN")
        self.assertTrue(system_role.is_system_role)
        self.assertIsNone(system_role.company)

    def test_role_detail_update_delete(self):
        detail_url = reverse("role-detail", kwargs={"pk": self.role.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["name"], "Admin")
        self.assertEqual(get_res.data["data"]["code"], "ADMIN")

        # PUT update
        update_payload = {
            "name": "Super Admin",
            "description": "Updated description",
            "company": self.company.id
        }
        put_res = self.client.put(detail_url, update_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["name"], "Super Admin")
        self.assertEqual(put_res.data["data"]["code"], "SUPER_ADMIN")

        # PATCH update name
        patch_res = self.client.patch(detail_url, {"name": "Chief Executive"}, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["data"]["name"], "Chief Executive")
        self.assertEqual(patch_res.data["data"]["code"], "CHIEF_EXECUTIVE")

        # DELETE assigned role (should fail with 400 due to ProtectedError)
        del_assigned_res = self.client.delete(detail_url)
        self.assertEqual(del_assigned_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(del_assigned_res.data["success"])

        # DELETE unassigned role (should succeed with 200 OK)
        unassigned_role = Role.objects.create(company=self.company, name="Unassigned Role")
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
            company=self.company,
            name="HR Manager",
            description="HR Manager role"
        )
        self.permission1 = Permission.objects.create(
            resource="employee",
            action="create",
            description="Create employee"
        )
        self.permission2 = Permission.objects.create(
            resource="employee",
            action="read",
            description="Read employee"
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
        self.assertEqual(response.data["data"]["permission_name"], "employee.create")

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
        self.assertEqual(get_res.data["data"]["permission_name"], "employee.create")

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(RolePermission.objects.filter(pk=rp.pk).exists())



