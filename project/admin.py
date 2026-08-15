from django.contrib import admin
from .models import Project, ProjectMember


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
        'employee__first_name',
        'employee__last_name',
        'role_in_project',
    )
    ordering = ('-created_at',)



