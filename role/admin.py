from django.contrib import admin
from .models import Role, RolePermission, RolePermissionSet


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1


class RolePermissionSetInline(admin.TabularInline):
    model = RolePermissionSet
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name')
    list_filter = ('created_at',)
    inlines = [RolePermissionInline, RolePermissionSetInline]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission', 'created_at', 'updated_at')
    search_fields = ('role__name', 'permission__name', 'permission__display_name', 'permission__code', 'permission__action')
    list_filter = ('created_at',)


@admin.register(RolePermissionSet)
class RolePermissionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission_set', 'created_at')
    search_fields = ('role__name', 'permission_set__name', 'permission_set__display_name', 'permission_set__code')
    list_filter = ('created_at',)



