from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from permission.models import Permission


class PermissionApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)
        self.permission = Permission.objects.create(
            name="employee.create",
            resource="employee",
            action="create",
            description="Allows creating employees"
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
                resource=f"resource_{i}",
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
                resource=f"custom_{i}",
                action="update"
            )
        response = self.client.get(f"{self.list_create_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 2)

    def test_filter_permissions_by_search_resource_and_action(self):
        Permission.objects.create(
            name="project.read",
            resource="project",
            action="read",
            description="View projects"
        )
        Permission.objects.create(
            name="project.delete",
            resource="project",
            action="delete",
            description="Remove projects"
        )

        # Search filter
        res_search = self.client.get(f"{self.list_create_url}?search=View projects")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_search.data["data"]["results"]), 1)
        self.assertEqual(res_search.data["data"]["results"][0]["name"], "project.read")

        # Resource filter
        res_resource = self.client.get(f"{self.list_create_url}?resource=project")
        self.assertEqual(res_resource.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_resource.data["data"]["results"]), 2)

        # Action filter
        res_action = self.client.get(f"{self.list_create_url}?action=delete")
        self.assertEqual(res_action.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_action.data["data"]["results"]), 1)
        self.assertEqual(res_action.data["data"]["results"][0]["name"], "project.delete")

    def test_create_permission_explicit_name(self):
        payload = {
            "name": "task.create",
            "resource": "task",
            "action": "create",
            "description": "Create new tasks"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "task.create")
        self.assertEqual(response.data["data"]["resource"], "task")
        self.assertEqual(response.data["data"]["action"], "create")

    def test_create_permission_auto_generated_name(self):
        payload = {
            "resource": "department",
            "action": "update",
            "description": "Update department details"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["name"], "department.update")

    def test_create_permission_validation_error(self):
        payload = {
            "resource": "",
            "action": "create"
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("resource", response.data["errors"])

    def test_permission_detail_get_put_patch_delete(self):
        detail_url = reverse("permission-detail", kwargs={"pk": self.permission.pk})

        # GET detail
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["data"]["name"], "employee.create")

        # PUT update
        put_payload = {
            "name": "employee.write",
            "resource": "employee",
            "action": "write",
            "description": "Updated employee write"
        }
        put_res = self.client.put(detail_url, put_payload, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["data"]["name"], "employee.write")
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
