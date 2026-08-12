from django.contrib import admin
from .models import Project


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
