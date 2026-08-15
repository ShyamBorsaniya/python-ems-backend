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

    def __str__(self):
        return self.username
