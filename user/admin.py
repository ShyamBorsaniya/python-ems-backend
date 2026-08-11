from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "company", "role", "is_staff")
    list_filter = ("company", "role", "is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "phone", "profile_image")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "email", "first_name", "last_name")}),
    )

