from django.contrib import admin
from .models import Employee


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
