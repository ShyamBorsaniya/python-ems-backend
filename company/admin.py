from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from company.models import (
    Company, User, Department, DepartmentPermissionSet,
    Designation, DesignationPermissionSet, Role, RolePermissionSet,
    Permission, Project, ProjectMember, Employee, Module,
    PermissionSet, PermissionSetPermission
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'country')
    search_fields = ('name', 'code', 'email', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "company", "role", "status", "is_staff")
    list_filter = ("status", "company", "role", "is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "status", "phone", "profile_photo_url", "last_login_at")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Company & Role Info", {"fields": ("company", "role", "status", "email", "first_name", "last_name")}),
    )


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


class RolePermissionSetInline(admin.TabularInline):
    model = RolePermissionSet
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name')
    list_filter = ('created_at',)
    inlines = [RolePermissionSetInline]


@admin.register(RolePermissionSet)
class RolePermissionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission_set', 'created_at')
    search_fields = ('role__name', 'permission_set__name', 'permission_set__display_name', 'permission_set__code')
    list_filter = ('created_at',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'code', 'action', 'module', 'company', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name', 'code', 'action', 'description')
    list_filter = ('action', 'module', 'company', 'created_at')


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'company',
        'status',
        'priority',
        'budget',
        'start_date',
        'end_date',
        'created_at',
    )
    list_filter = (
        'status',
        'priority',
        'company',
    )
    search_fields = (
        'name',
        'code',
        'description',
    )
    ordering = ('-created_at',)
    inlines = [ProjectMemberInline]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project',
        'employee',
        'role_in_project',
        'assigned_at',
        'removed_at',
        'created_at',
    )
    list_filter = (
        'project',
        'role_in_project',
        'assigned_at',
    )
    search_fields = (
        'project__name',
        'project__code',
        'employee__user__first_name',
        'employee__user__last_name',
        'role_in_project',
    )
    ordering = ('-created_at',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'code',
        'company',
        'department',
        'designation',
        'employment_type',
        'employment_status',
        'joining_date',
        'created_at'
    )
    list_filter = (
        'employment_status',
        'employment_type',
        'gender',
        'company',
        'department',
        'designation'
    )
    search_fields = (
        'code',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'emergency_contact_name'
    )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'name', 'code', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'display_name', 'code', 'description')


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
