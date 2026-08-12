from django.db import models


class Permission(models.Model):
    name = models.CharField(max_length=255, blank=True)
    resource = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Permissions"
        unique_together = ('resource', 'action')

    def save(self, *args, **kwargs):
        if not self.name and self.resource and self.action:
            self.name = f"{self.resource.strip().lower()}.{self.action.strip().lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"{self.resource}.{self.action}"
