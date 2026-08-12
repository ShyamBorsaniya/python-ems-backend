from django.contrib import admin
from .models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'resource', 'action', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'resource', 'action', 'description')
    list_filter = ('resource', 'action', 'created_at')
