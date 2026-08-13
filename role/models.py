from django.db import models
from django.utils.text import slugify
from company.models import Company
from permission.models import Permission


class Role(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='roles',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_system_role = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Roles"

    def _generate_code(self):
        base_code = slugify(self.name).replace('-', '_').upper()
        if not base_code:
            base_code = "ROLE"

        code_candidate = base_code
        counter = 1
        queryset = Role.objects.filter(code=code_candidate)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.exists():
            code_candidate = f"{base_code}_{counter}"
            counter += 1
            queryset = Role.objects.filter(code=code_candidate)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        return code_candidate

    def save(self, *args, **kwargs):
        if self.name:
            if not self.pk:
                self.code = self._generate_code()
            else:
                old_instance = Role.objects.filter(pk=self.pk).first()
                if not self.code or (old_instance and old_instance.name != self.name):
                    self.code = self._generate_code()
        super().save(*args, **kwargs)

    def __str__(self):
        company_name = self.company.name if self.company else "System"
        return f"{self.name} ({company_name})"


class RolePermission(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Role Permissions"
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


