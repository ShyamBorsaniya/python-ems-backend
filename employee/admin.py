from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_code',
        'designation',
        'company',
        'department',
        'employment_type',
        'status',
        'joining_date',
        'created_at'
    )
    list_filter = ('employment_type', 'status', 'gender', 'company', 'department')
    search_fields = ('employee_code', 'designation', 'phone', 'emergency_contact_name')
    ordering = ('-created_at',)
