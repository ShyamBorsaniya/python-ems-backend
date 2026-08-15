from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from company.models import User, Company, Module, Permission


class PermissionApiTests(APITestCase):

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
        self.module = Module.objects.create(
            company=self.company,
            name="Project Module",
            display_name="Project Module",
            code="proj_mod"
        )
        self.permission = Permission.objects.create(
            company=self.company,
            module=self.module,
            name="project.create",
            display_name="Create Project",
            code="project:create",
            action="create",
            description="Allows creating projects"
        )
        self.list_create_url = reverse("permission-list-create")

    def test_list_permissions_paginated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertEqual(response.data["data"]["pagination"]["page"], 1)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 10)
        self.assertEqual(response.data["data"]["pagination"]["total_items"], 1)

    def test_list_permissions_pagination_multiple_pages(self):
        # Create 11 more permissions (12 total)
        for i in range(11):
            Permission.objects.create(
                company=self.company,
                module=self.module,
                name=f"permission_{i}",
                display_name=f"Permission {i}",
                code=f"code_{i}",
                action="read",
                description=f"Description {i}"
            )

        # Page 1
        page1 = self.client.get(self.list_create_url)
        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page1.data["data"]["results"]), 10)
        self.assertEqual(page1.data["data"]["pagination"]["total_items"], 12)
        self.assertEqual(page1.data["data"]["pagination"]["total_pages"], 2)
        self.assertEqual(page1.data["data"]["pagination"]["next_page"], 2)

        # Page 2
        page2 = self.client.get(f"{self.list_create_url}?page=2")
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data["data"]["results"]), 2)
        self.assertEqual(page2.data["data"]["pagination"]["page"], 2)
        self.assertIsNone(page2.data["data"]["pagination"]["next_page"])

    def test_list_permissions_custom_page_size(self):
        for i in range(3):
            Permission.objects.create(
                module=self.module,
                name=f"custom_{i}",
                display_name=f"Custom {i}",
                code=f"custom_code_{i}",
                action="update"
            )
        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)

    def test_filter_permissions_by_search_module_and_action(self):
        Permission.objects.create(
            module=self.module,
            name="task.read",
            display_name="Read Task",
            code="task:read",
            action="read",
            description="View tasks"
        )
        Permission.objects.create(
            module=self.module,
            name="task.delete",
            display_name="Delete Task",
            code="task:delete",
            action="delete",
            description="Remove tasks"
        )

        # Search filter
        res_search = self.client.get(f"{self.list_create_url}?search=View tasks")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_search.data["data"]["results"]), 1)
        self.assertEqual(res_search.data["data"]["results"][0]["name"], "task.read")

        # Module filter
        res_module = self.client.get(f"{self.list_create_url}?module={self.module.id}")
        self.assertEqual(res_module.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_module.data["data"]["results"]), 3)

        # Action filter
        res_action = self.client.get(f"{self.list_create_url}?action=delete")
        self.assertEqual(res_action.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_action.data["data"]["results"]), 1)
        self.assertEqual(res_action.data["data"]["results"][0]["name"], "task.delete")

    def test_create_permission_success(self):
        payload = {
            "company": self.company.id,
            "module": self.module.id,
            "name": "task.create",
            "display_name": "Create Task",
            "code": "task:create",
            "action": "create",
            "description": "Create new tasks"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "task.create")
        self.assertEqual(response.data["data"]["display_name"], "Create Task")
        self.assertEqual(response.data["data"]["code"], "task:create")
        self.assertEqual(response.data["data"]["action"], "create")

    def test_create_permission_validation_error(self):
        payload = {
            "name": "task.create",
            "display_name": "",
            "code": "",
            "action": "create"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("module", response.data["errors"])

    def test_permission_detail_get_put_patch_delete(self):
        detail_url = reverse("permission-detail", kwargs={"pk": self.permission.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["name"], "project.create")

        # PUT update
        put_payload = {
            "company": self.company.id,
            "module": self.module.id,
            "name": "project.write",
            "display_name": "Write Project",
            "code": "project:write",
            "action": "write",
            "description": "Updated project write"
        }
        put_res = self.client.put(detail_url, put_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["name"], "project.write")
        self.assertEqual(put_res.data["data"]["code"], "project:write")
        self.assertEqual(put_res.data["data"]["action"], "write")

        # PATCH update
        patch_payload = {
            "description": "Patched description"
        }
        patch_res = self.client.patch(detail_url, patch_payload, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["data"]["description"], "Patched description")

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Permission.objects.filter(pk=self.permission.pk).exists())
