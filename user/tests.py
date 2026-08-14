from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User, UserStatus
from company.models import Company
from role.models import Role


class UserAuthTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Corp",
            email="info@testcorp.com"
        )
        self.role = Role.objects.create(
            name="Software Engineer",
            display_name="Engineers software"
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
            "company": self.company.id,
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
        self.assertIsInstance(response.data["data"]["user"]["company"], dict)
        self.assertEqual(response.data["data"]["user"]["company"]["id"], self.company.id)
        self.assertEqual(response.data["data"]["user"]["company"]["name"], "Test Corp")

    def test_user_registration_pending_status(self):
        data = self.user_data.copy()
        data["status"] = UserStatus.PENDING
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status_code"], 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "you are registered successfull please wait untill admin can approve")
        self.assertNotIn("data", response.data)

    def test_user_registration_without_role_fails(self):
        data = self.user_data.copy()
        del data["role"]
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("role", response.data["errors"])

    def test_user_registration_without_company_fails(self):
        data = self.user_data.copy()
        del data["company"]
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("company", response.data["errors"])

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
        self.assertIsInstance(response.data["data"]["user"]["company"], dict)
        self.assertEqual(response.data["data"]["user"]["company"]["id"], self.company.id)
        self.assertEqual(response.data["data"]["user"]["company"]["name"], "Test Corp")
        self.assertEqual(response.data["data"]["user"]["company"]["email"], "info@testcorp.com")

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
        self.assertIsInstance(response.data["data"]["user"]["company"], dict)
        self.assertEqual(response.data["data"]["user"]["company"]["name"], "Test Corp")

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

    def test_login_inactive_user(self):
        user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            is_active=False
        )
        login_payload = {
            "username": "inactiveuser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertIn("your account has been inactivated please contact to admin", response.data["errors"]["non_field_errors"])

    def test_login_pending_user(self):
        User.objects.create_user(
            username="pendinguser",
            email="pending@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.PENDING
        )
        login_payload = {
            "username": "pendinguser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertIn("your account has been waiting to approval", response.data["errors"]["non_field_errors"])

    def test_login_rejected_user(self):
        User.objects.create_user(
            username="rejecteduser",
            email="rejected@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.REJECTED
        )
        login_payload = {
            "username": "rejecteduser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertIn("your account has been terminited, contact to admin for ferther query", response.data["errors"]["non_field_errors"])

    def test_list_users_unauthenticated(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_authenticated(self):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("results", response.data["data"])
        self.assertIn("pagination", response.data["data"])
        self.assertLessEqual(len(response.data["data"]["results"]), 5)
        self.assertEqual(response.data["data"]["pagination"]["page_size"], 5)

    def test_list_users_paginates_to_five_per_page(self):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        for index in range(6):
            User.objects.create_user(
                username=f"user{index}",
                email=f"user{index}@example.com",
                password="Password123!",
                role=self.role,
                company=self.company
            )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")

        first_page = self.client.get(url)
        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(len(first_page.data["data"]["results"]), 5)
        self.assertEqual(first_page.data["data"]["pagination"]["page"], 1)
        self.assertEqual(first_page.data["data"]["pagination"]["next_page"], 2)

        second_page = self.client.get(f"{url}?page=2")
        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(len(second_page.data["data"]["results"]), 2)
        self.assertEqual(second_page.data["data"]["pagination"]["page"], 2)
        self.assertIsNone(second_page.data["data"]["pagination"]["next_page"])

    def test_list_users_filter_by_company(self):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = f"{reverse('user-list')}?company={self.company.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["company"]["id"], self.company.id)

    def test_get_user_detail(self):
        user = User.objects.create_user(
            username="detailuser",
            email="detailuser@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "detailuser")
        self.assertEqual(response.data["data"]["company"]["id"], self.company.id)

    def test_update_user_put(self):
        user = User.objects.create_user(
            username="updateuser",
            email="updateuser@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        payload = {
            "username": "updateuser",
            "email": "updateuser_new@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "role": self.role.id,
            "company": self.company.id,
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["first_name"], "Updated")
        self.assertEqual(response.data["data"]["email"], "updateuser_new@example.com")
        self.assertEqual(response.data["data"]["company"]["id"], self.company.id)

    def test_update_user_patch(self):
        user = User.objects.create_user(
            username="patchuser",
            email="patchuser@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
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
            role=self.role,
            company=self.company
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

    def test_restore_soft_deleted_user(self):
        user = User.objects.create_user(
            username="restoreuser",
            email="restore@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        self.client.force_authenticate(user=user)
        url = reverse("user-restore", kwargs={"pk": user.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["is_active"])

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_role_protected_on_delete(self):
        from django.db.models import ProtectedError
        user = User.objects.create_user(
            username="roleuser",
            email="roleuser@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        with self.assertRaises(ProtectedError):
            self.role.delete()

    def test_user_default_status(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["user"]["status"], "approved")

    def test_update_user_status(self):
        user = User.objects.create_user(
            username="statususer",
            email="statususer@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = self.client.patch(url, {"status": "rejected"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "rejected")

    def test_list_users_filter_by_status(self):
        user1 = User.objects.create_user(
            username="user_pending",
            email="pending@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status="pending"
        )
        user2 = User.objects.create_user(
            username="user_approved",
            email="approved@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status="approved"
        )
        self.client.force_authenticate(user=user2)
        url = f"{reverse('user-list')}?status=pending"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["username"], "user_pending")

    def test_get_company_pending_users(self):
        user_pending = User.objects.create_user(
            username="pending_comp_user",
            email="pending_comp@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.PENDING
        )
        other_company = Company.objects.create(name="Other Corp", code="OTHER_CORP", email="other@test.com")
        User.objects.create_user(
            username="other_pending_user",
            email="other_pending@example.com",
            password="Password123!",
            role=self.role,
            company=other_company,
            status=UserStatus.PENDING
        )
        auth_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.APPROVED
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-pending-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], "pending_comp_user")

    def test_get_pending_users_unauthenticated(self):
        url = reverse("user-pending-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_user(self):
        user_pending = User.objects.create_user(
            username="to_approve",
            email="to_approve@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.PENDING
        )
        auth_user = User.objects.create_user(
            username="approver",
            email="approver@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.APPROVED
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-approve", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], UserStatus.APPROVED)
        user_pending.refresh_from_db()
        self.assertEqual(user_pending.status, UserStatus.APPROVED)

    def test_reject_user(self):
        user_pending = User.objects.create_user(
            username="to_reject",
            email="to_reject@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.PENDING
        )
        auth_user = User.objects.create_user(
            username="rejector",
            email="rejector@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.APPROVED
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-reject", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], UserStatus.REJECTED)
        user_pending.refresh_from_db()
        self.assertEqual(user_pending.status, UserStatus.REJECTED)

    def test_approve_reject_unauthenticated(self):
        url_approve = reverse("user-approve", kwargs={"pk": 1})
        response = self.client.post(url_approve)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url_reject = reverse("user-reject", kwargs={"pk": 1})
        response = self.client.post(url_reject)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)






