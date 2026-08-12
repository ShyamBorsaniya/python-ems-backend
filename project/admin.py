from django.contrib import admin
from .models import Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'company',
        'department',
        'status',
        'priority',
        'project_manager',
        'budget',
        'start_date',
        'end_date',
        'created_at',
    )
    list_filter = (
        'status',
        'priority',
        'company',
        'department',
    )
    search_fields = (
        'name',
        'code',
        'description',
    )
    ordering = ('-created_at',)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project',
        'employee',
        'role',
        'joined_at',
        'left_at',
        'created_at',
    )
    list_filter = (
        'role',
        'joined_at',
        'project',
    )
    search_fields = (
        'role',
        'project__name',
        'employee__employee_code',
    )
    ordering = ('-created_at',)

