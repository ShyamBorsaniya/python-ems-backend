from django.contrib import admin
from .models import PermissionSet, PermissionSetPermission


@admin.register(PermissionSet)
class PermissionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'code', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name', 'code', 'description')
    list_filter = ('company', 'created_at')


@admin.register(PermissionSetPermission)
class PermissionSetPermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'permission_set', 'permission', 'created_at')
    search_fields = ('permission_set__name', 'permission_set__code', 'permission__name', 'permission__code')
    list_filter = ('permission_set', 'created_at')

