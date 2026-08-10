from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User


class UserAuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status_code"], 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "User registered successfully")
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["user"]["username"], "testuser")

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


