from django.db import models


class Module(models.Model):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='modules',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Modules"
        unique_together = ['company', 'code']

    def __str__(self):
        return f"{self.display_name} ({self.code})"
