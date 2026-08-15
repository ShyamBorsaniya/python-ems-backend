from django.contrib import admin
from .models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'code', 'action', 'module', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name', 'code', 'action', 'description')
    list_filter = ('action', 'module', 'company', 'created_at')

