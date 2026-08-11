from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from company.models import Company
from role.models import Role


class UserAuthTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Corp",
            email="info@testcorp.com"
        )
        self.role = Role.objects.create(
            company=self.company,
            name="Software Engineer",
            description="Engineers software"
        )
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User",
            "role": self.role.id,
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status_code"], 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "User registered successfully")
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["user"]["username"], "testuser")
        self.assertEqual(response.data["data"]["user"]["role"], self.role.id)
        self.assertEqual(response.data["data"]["user"]["role_name"], "Software Engineer")

    def test_user_registration_without_role_fails(self):
        data = self.user_data.copy()
        del data["role"]
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("role", response.data["errors"])

    def test_user_login_with_username(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_payload = {
            "username": "testuser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_code"], 200)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])
        self.assertEqual(response.data["data"]["user"]["role"], self.role.id)
        self.assertEqual(response.data["data"]["user"]["role_name"], "Software Engineer")

    def test_user_login_with_email(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_payload = {
            "username": "testuser@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_code"], 200)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])

    def test_login_invalid_credentials(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_payload = {
            "username": "testuser",
            "password": "WrongPassword",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status_code"], 400)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)

    def test_list_users_unauthenticated(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_authenticated(self):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="Password123!",
            role=self.role
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIsInstance(response.data["data"], list)

    def test_get_user_detail(self):
        user = User.objects.create_user(
            username="detailuser",
            email="detailuser@example.com",
            password="Password123!",
            role=self.role
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "detailuser")

    def test_update_user_put(self):
        user = User.objects.create_user(
            username="updateuser",
            email="updateuser@example.com",
            password="Password123!",
            role=self.role
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        payload = {
            "username": "updateuser",
            "email": "updateuser_new@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "role": self.role.id,
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["first_name"], "Updated")
        self.assertEqual(response.data["data"]["email"], "updateuser_new@example.com")

    def test_update_user_patch(self):
        user = User.objects.create_user(
            username="patchuser",
            email="patchuser@example.com",
            password="Password123!",
            role=self.role
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        payload = {"first_name": "Patched"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["first_name"], "Patched")

    def test_soft_delete_user(self):
        user = User.objects.create_user(
            username="softdeleteuser",
            email="softdelete@example.com",
            password="Password123!",
            role=self.role
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(response.data["data"]["is_active"])
        # Verify user still exists in database, but is deactivated
        user.refresh_from_db()
        self.assertFalse(user.is_active)


