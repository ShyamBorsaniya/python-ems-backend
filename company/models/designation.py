from django.db import models


class Designation(models.Model):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='designations'
    )
    department = models.ForeignKey(
        'company.Department',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='designations'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, default='')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Designations"
        unique_together = ['company', 'code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class DesignationPermissionSet(models.Model):
    designation = models.ForeignKey(
        'company.Designation',
        on_delete=models.CASCADE,
        related_name='designation_permission_sets'
    )
    permission_set = models.ForeignKey(
        'company.PermissionSet',
        on_delete=models.CASCADE,
        related_name='designation_permission_sets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Designation Permission Sets"
        unique_together = ('designation', 'permission_set')

    def __str__(self):
        return f"{self.designation.name} - {self.permission_set.name}"
