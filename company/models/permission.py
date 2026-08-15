from django.db import models


class Permission(models.Model):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='permissions',
        null=True,
        blank=True
    )
    module = models.ForeignKey(
        'company.Module',
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Permissions"
        unique_together = ['module', 'code']

    def __str__(self):
        return f"{self.display_name} ({self.code})"
