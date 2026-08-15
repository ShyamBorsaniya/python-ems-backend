from django.db import models


class PermissionSet(models.Model):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='permission_sets',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Permission Sets"
        unique_together = ['company', 'code']

    def __str__(self):
        return f"{self.display_name} ({self.code})"


class PermissionSetPermission(models.Model):
    permission_set = models.ForeignKey(
        'company.PermissionSet',
        on_delete=models.CASCADE,
        related_name='permission_set_permissions'
    )
    permission = models.ForeignKey(
        'company.Permission',
        on_delete=models.CASCADE,
        related_name='permission_set_permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Permission Set Permissions"
        unique_together = ('permission_set', 'permission')

    def __str__(self):
        return f"{self.permission_set.name} - {self.permission.name}"
