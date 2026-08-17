from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from company.models import User, UserStatus, Company, Role


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

    def test_user_registration_inactive_status(self):
        data = self.user_data.copy()
        data["status"] = UserStatus.INACTIVE
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status_code"], 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "you are registered successfully but your account is inactive, please wait until admin can activate it")
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

    def test_user_login_returns_permissions(self):
        # 1. Create a module and a permission
        from company.models import Module, Permission, PermissionSet, RolePermissionSet
        module = Module.objects.create(
            company=self.company,
            name="Employee Module",
            code="emp_mod"
        )
        permission1 = Permission.objects.create(
            company=self.company,
            module=module,
            name="employee.view",
            code="employee:view",
            action="view"
        )
        permission2 = Permission.objects.create(
            company=self.company,
            module=module,
            name="employee.create",
            code="employee:create",
            action="create"
        )
        # 2. Create permission set
        permission_set = PermissionSet.objects.create(
            company=self.company,
            name="Employee Operations",
            code="emp_ops"
        )
        # Link permissions to permission set
        from company.models import PermissionSetPermission
        PermissionSetPermission.objects.create(permission_set=permission_set, permission=permission1)
        PermissionSetPermission.objects.create(permission_set=permission_set, permission=permission2)

        # 3. Link permission set to role
        RolePermissionSet.objects.create(role=self.role, permission_set=permission_set)

        # 4. Register and Login the user
        self.client.post(self.register_url, self.user_data, format="json")
        login_payload = {
            "username": "testuser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data["data"]["user"]
        self.assertIn("permissions", user_data)
        
        # Verify permissions list contains the module and nested permissions
        self.assertEqual(len(user_data["permissions"]), 1)
        module_group = user_data["permissions"][0]
        self.assertEqual(module_group["module_name"], "Employee Module")
        self.assertEqual(len(module_group["permissions"]), 2)
        
        codes = [p["code"] for p in module_group["permissions"]]
        self.assertIn("employee:view", codes)
        self.assertIn("employee:create", codes)

        # Check permission structure fields
        perm_item = module_group["permissions"][0]
        self.assertEqual(perm_item["name"], "employee.view" if perm_item["code"] == "employee:view" else "employee.create")
        self.assertIn("display_name", perm_item)
        self.assertIn("action", perm_item)

    def test_user_permissions_from_department_and_designation(self):
        from company.models import Module, Permission, PermissionSet, Department, Designation, DepartmentPermissionSet, DesignationPermissionSet, Employee
        # Create department & designation
        department = Department.objects.create(company=self.company, name="Engineering", code="ENG")
        designation = Designation.objects.create(company=self.company, department=department, name="Tech Lead", code="TL")
        
        # Create user
        user = User.objects.create_user(
            username="empuser",
            email="empuser@example.com",
            password="Password123!",
            company=self.company
        )
        
        # Create employee record linking to user, department, designation
        from datetime import date
        Employee.objects.create(
            user=user,
            company=self.company,
            code="EMP001",
            department=department,
            designation=designation,
            joining_date=date.today()
        )
        
        # Create module and permissions
        module = Module.objects.create(company=self.company, name="Admin Module", code="admin_mod")
        dept_perm = Permission.objects.create(
            company=self.company,
            module=module,
            name="dept.view",
            code="dept:view",
            action="view"
        )
        desg_perm = Permission.objects.create(
            company=self.company,
            module=module,
            name="desg.edit",
            code="desg:edit",
            action="edit"
        )
        
        # Create permission sets and link permissions
        dept_ps = PermissionSet.objects.create(company=self.company, name="Dept PS", code="dept_ps")
        desg_ps = PermissionSet.objects.create(company=self.company, name="Desg PS", code="desg_ps")
        
        from company.models import PermissionSetPermission
        PermissionSetPermission.objects.create(permission_set=dept_ps, permission=dept_perm)
        PermissionSetPermission.objects.create(permission_set=desg_ps, permission=desg_perm)
        
        # Associate permission sets with department and designation
        DepartmentPermissionSet.objects.create(department=department, permission_set=dept_ps)
        DesignationPermissionSet.objects.create(designation=designation, permission_set=desg_ps)
        
        # Login
        login_payload = {
            "username": "empuser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data["data"]["user"]
        self.assertIn("permissions", user_data)
        
        # Verify permissions list contains the module and nested permissions
        self.assertEqual(len(user_data["permissions"]), 1)
        module_group = user_data["permissions"][0]
        self.assertEqual(module_group["module_name"], "Admin Module")
        self.assertEqual(len(module_group["permissions"]), 2)
        
        codes = [p["code"] for p in module_group["permissions"]]
        self.assertIn("dept:view", codes)
        self.assertIn("desg:edit", codes)

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

    def test_login_inactive_user_status(self):
        User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.INACTIVE
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

    def test_login_locked_user(self):
        User.objects.create_user(
            username="lockeduser",
            email="locked@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.LOCKED
        )
        login_payload = {
            "username": "lockeduser",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertIn("your account has been locked, contact to admin for further query", response.data["errors"]["non_field_errors"])

    def test_list_users_unauthenticated(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_authenticated(self):
        user = User.objects.create_superuser(
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

    def test_list_users_excludes_superuser_for_regular_user(self):
        from company.models import Module, Permission, PermissionSet, RolePermissionSet, PermissionSetPermission
        module, _ = Module.objects.get_or_create(company=self.company, code="user_management", defaults={"name": "User Module"})
        permission, _ = Permission.objects.get_or_create(company=self.company, module=module, action="view", defaults={"name": "user.view", "code": "user:view"})
        perm_set = PermissionSet.objects.create(company=self.company, name="User View Ex", code="user_view_ex")
        PermissionSetPermission.objects.create(permission_set=perm_set, permission=permission)
        RolePermissionSet.objects.create(role=self.role, permission_set=perm_set)

        regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            is_superuser=False
        )
        superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="Password123!"
        )
        self.client.force_authenticate(user=regular_user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u["username"] for u in response.data["data"]["results"]]
        self.assertNotIn("adminuser", usernames)
        self.assertIn("regularuser", usernames)

    def test_list_users_includes_superuser_for_superuser(self):
        superuser = User.objects.create_superuser(
            username="adminuser2",
            email="admin2@example.com",
            password="Password123!"
        )
        self.client.force_authenticate(user=superuser)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u["username"] for u in response.data["data"]["results"]]
        self.assertIn("adminuser2", usernames)

    def test_dynamic_permission_check_regular_user_with_permission(self):
        from company.models import Module, Permission, PermissionSet, RolePermissionSet, PermissionSetPermission
        module, _ = Module.objects.get_or_create(company=self.company, code="user_management", defaults={"name": "User Module"})
        permission, _ = Permission.objects.get_or_create(company=self.company, module=module, action="view", defaults={"name": "user.view", "code": "user:view"})
        perm_set = PermissionSet.objects.create(company=self.company, name="User View Dyn", code="user_view_dyn")
        PermissionSetPermission.objects.create(permission_set=perm_set, permission=permission)
        role_dyn = Role.objects.create(name="Dyn Role", display_name="Dynamic Role")
        RolePermissionSet.objects.create(role=role_dyn, permission_set=perm_set)

        user = User.objects.create_user(
            username="permuser",
            email="permuser@example.com",
            password="Password123!",
            role=role_dyn,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dynamic_permission_check_regular_user_without_permission_denied(self):
        role_no_perm = Role.objects.create(name="No Perm Role", display_name="No permissions")
        user = User.objects.create_user(
            username="nopermuser",
            email="noperm@example.com",
            password="Password123!",
            role=role_no_perm,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_permission_regular_user_without_permission_denied(self):
        role_no_perm = Role.objects.create(name="No Perm Role 2", display_name="No permissions")
        user = User.objects.create_user(
            username="nopermuser2",
            email="noperm2@example.com",
            password="Password123!",
            role=role_no_perm,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_permission_regular_user_with_permission_allowed(self):
        from company.models import Module, Permission, PermissionSet, RolePermissionSet, PermissionSetPermission
        module, _ = Module.objects.get_or_create(company=self.company, code="user_management", defaults={"name": "User Module"})
        permission, _ = Permission.objects.get_or_create(company=self.company, module=module, action="create", defaults={"name": "user.create", "code": "user:create"})
        perm_set = PermissionSet.objects.create(company=self.company, name="User Create Dyn", code="user_create_dyn")
        PermissionSetPermission.objects.create(permission_set=perm_set, permission=permission)
        role_create = Role.objects.create(name="Create Role", display_name="Create Role")
        RolePermissionSet.objects.create(role=role_create, permission_set=perm_set)

        user = User.objects.create_user(
            username="creatoruser",
            email="creator@example.com",
            password="Password123!",
            role=role_create,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-list")
        data = self.user_data.copy()
        data["username"] = "newcreateduser"
        data["email"] = "newcreated@example.com"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_users_paginates_to_five_per_page(self):
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        user = User.objects.create_superuser(
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
        self.assertEqual(response.data["data"]["user"]["status"], "active")

    def test_update_user_status(self):
        user = User.objects.create_superuser(
            username="statususer",
            email="statususer@example.com",
            password="Password123!",
            role=self.role,
            company=self.company
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", kwargs={"pk": user.pk})
        response = self.client.patch(url, {"status": "locked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "locked")

    def test_list_users_filter_by_status(self):
        user1 = User.objects.create_user(
            username="user_inactive",
            email="inactive@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status="inactive"
        )
        user2 = User.objects.create_superuser(
            username="user_active",
            email="active@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status="active"
        )
        self.client.force_authenticate(user=user2)
        url = f"{reverse('user-list')}?status=inactive"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertEqual(response.data["data"]["results"][0]["username"], "user_inactive")

    def test_get_company_pending_users(self):
        user_pending = User.objects.create_user(
            username="pending_comp_user",
            email="pending_comp@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.INACTIVE
        )
        other_company = Company.objects.create(name="Other Corp", code="OTHER_CORP", email="other@test.com")
        User.objects.create_user(
            username="other_pending_user",
            email="other_pending@example.com",
            password="Password123!",
            role=self.role,
            company=other_company,
            status=UserStatus.INACTIVE
        )
        auth_user = User.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.ACTIVE
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
            status=UserStatus.INACTIVE
        )
        auth_user = User.objects.create_superuser(
            username="approver",
            email="approver@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.ACTIVE
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-approve", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], UserStatus.ACTIVE)
        user_pending.refresh_from_db()
        self.assertEqual(user_pending.status, UserStatus.ACTIVE)

    def test_reject_user(self):
        user_pending = User.objects.create_user(
            username="to_reject",
            email="to_reject@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.INACTIVE
        )
        auth_user = User.objects.create_superuser(
            username="rejector",
            email="rejector@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.ACTIVE
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-reject", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], UserStatus.LOCKED)
        user_pending.refresh_from_db()
        self.assertEqual(user_pending.status, UserStatus.LOCKED)

    def test_approve_reject_unauthenticated(self):
        url_approve = reverse("user-approve", kwargs={"pk": 1})
        response = self.client.post(url_approve)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url_reject = reverse("user-reject", kwargs={"pk": 1})
        response = self.client.post(url_reject)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_user_with_permission(self):
        from company.models import Module, Permission, PermissionSet, RolePermissionSet, PermissionSetPermission
        module = Module.objects.create(
            company=self.company,
            name="User Management",
            code="user_management"
        )
        permission = Permission.objects.create(
            company=self.company,
            module=module,
            name="user.approve",
            code="user:approve",
            action="approve"
        )
        permission_set = PermissionSet.objects.create(
            company=self.company,
            name="User Operations",
            code="user_ops"
        )
        PermissionSetPermission.objects.create(permission_set=permission_set, permission=permission)
        
        approver_role = Role.objects.create(
            name="User Manager",
            display_name="Manages Users"
        )
        RolePermissionSet.objects.create(role=approver_role, permission_set=permission_set)

        user_pending = User.objects.create_user(
            username="to_approve",
            email="to_approve@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.INACTIVE
        )
        auth_user = User.objects.create_user(
            username="approver",
            email="approver@example.com",
            password="Password123!",
            role=approver_role,
            company=self.company,
            status=UserStatus.ACTIVE
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-approve", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], UserStatus.ACTIVE)
        user_pending.refresh_from_db()
        self.assertEqual(user_pending.status, UserStatus.ACTIVE)

    def test_approve_user_without_permission_fails(self):
        user_pending = User.objects.create_user(
            username="to_approve",
            email="to_approve@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.INACTIVE
        )
        auth_user = User.objects.create_user(
            username="unauthorized_approver",
            email="unauth_approver@example.com",
            password="Password123!",
            role=self.role,
            company=self.company,
            status=UserStatus.ACTIVE
        )
        self.client.force_authenticate(user=auth_user)
        url = reverse("user-approve", kwargs={"pk": user_pending.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

