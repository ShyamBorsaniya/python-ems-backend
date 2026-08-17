from django.contrib.auth.models import AbstractUser
from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    LOCKED = 'locked', 'Locked'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_photo_url = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(
        'company.Role',
        on_delete=models.PROTECT,
        related_name='users',
        blank=True,
        null=True
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        related_name='users',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE
    )
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_all_permissions(self):
        from company.models import Permission
        from django.db.models import Q
        
        q_filters = Q()
        if self.role_id:
            q_filters |= Q(permission_set_permissions__permission_set__role_permission_sets__role_id=self.role_id)

        if hasattr(self, 'employee') and self.employee:
            employee = self.employee
            if employee.department_id:
                q_filters |= Q(permission_set_permissions__permission_set__department_permission_sets__department_id=employee.department_id)
            if employee.designation_id:
                q_filters |= Q(permission_set_permissions__permission_set__designation_permission_sets__designation_id=employee.designation_id)

        if not q_filters:
            return []

        permissions = Permission.objects.filter(q_filters).select_related('module').distinct()

        module_groups = {}
        for perm in permissions:
            module = perm.module
            if module.id not in module_groups:
                module_groups[module.id] = {
                    "module_name": module.name,
                    "permissions": []
                }
            module_groups[module.id]["permissions"].append({
                "id": perm.id,
                "name": perm.name,
                "display_name": perm.display_name,
                "code": perm.code,
                "action": perm.action
            })

        return list(module_groups.values())

    def has_permission(self, module_code, action):
        """
        Check dynamically if the user has permission for module and action.
        If user is a superuser (is_superuser=True), returns True.
        """
        if self.is_superuser:
            return True
        if not self.is_active:
            return False

        from company.models import Permission
        from django.db.models import Q

        q_filters = Q()
        if self.role_id:
            q_filters |= Q(permission_set_permissions__permission_set__role_permission_sets__role_id=self.role_id)

        if hasattr(self, 'employee') and self.employee:
            employee = self.employee
            if employee.department_id:
                q_filters |= Q(permission_set_permissions__permission_set__department_permission_sets__department_id=employee.department_id)
            if employee.designation_id:
                q_filters |= Q(permission_set_permissions__permission_set__designation_permission_sets__designation_id=employee.designation_id)

        if not q_filters:
            return False

        return Permission.objects.filter(
            q_filters,
            module__code__iexact=module_code,
            action__iexact=action
        ).exists()

    def __str__(self):
        return self.username

