from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "company", "role", "status", "is_staff")
    list_filter = ("status", "company", "role", "is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "status", "phone", "profile_photo_url", "last_login_at")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "status", "email", "first_name", "last_name")}),
    )

