from django.contrib import admin
from .models import Department, DepartmentPermissionSet


class DepartmentPermissionSetInline(admin.TabularInline):
    model = DepartmentPermissionSet
    extra = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'code', 'description', 'company__name')
    inlines = [DepartmentPermissionSetInline]


@admin.register(DepartmentPermissionSet)
class DepartmentPermissionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'permission_set', 'created_at')
    search_fields = ('department__name', 'department__code', 'permission_set__name', 'permission_set__display_name', 'permission_set__code')
    list_filter = ('created_at',)

