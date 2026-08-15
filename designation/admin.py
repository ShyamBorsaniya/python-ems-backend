from django.contrib import admin
from .models import Designation, DesignationPermissionSet


class DesignationPermissionSetInline(admin.TabularInline):
    model = DesignationPermissionSet
    extra = 1


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('company', 'department', 'name', 'code', 'is_active', 'created_at')
    list_filter = ('company', 'department', 'is_active')
    search_fields = ('name', 'code', 'description')
    inlines = [DesignationPermissionSetInline]


@admin.register(DesignationPermissionSet)
class DesignationPermissionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation', 'permission_set', 'created_at')
    search_fields = ('designation__name', 'designation__code', 'permission_set__name', 'permission_set__display_name', 'permission_set__code')
    list_filter = ('created_at',)

