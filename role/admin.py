from django.contrib import admin
from .models import Role, RolePermission


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'company', 'is_system_role', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description', 'company__name')
    list_filter = ('is_system_role', 'company', 'created_at')
    inlines = [RolePermissionInline]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission', 'created_at', 'updated_at')
    search_fields = ('role__name', 'permission__name', 'permission__resource', 'permission__action')
    list_filter = ('created_at',)


