from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class RolePermissionSet(models.Model):
    role = models.ForeignKey(
        'company.Role',
        on_delete=models.CASCADE,
        related_name='role_permission_sets'
    )
    permission_set = models.ForeignKey(
        'company.PermissionSet',
        on_delete=models.CASCADE,
        related_name='role_permission_sets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Role Permission Sets"
        unique_together = ('role', 'permission_set')

    def __str__(self):
        return f"{self.role.name} - {self.permission_set.name}"
