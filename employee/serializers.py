from rest_framework import serializers
from .models import Employee, EmploymentType, EmployeeStatus, Gender
from company.models import Company
from department.models import Department
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    department_name = serializers.SerializerMethodField()
    designation_name = serializers.ReadOnlyField(source='designation.name', allow_null=True)
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'user_username',
            'user_full_name',
            'company',
            'company_name',
            'department',
            'department_name',
            'employee_code',
            'designation',
            'designation_name',
            'joining_date',
            'employment_type',
            'date_of_birth',
            'gender',
            'phone',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name', 'department_name', 'designation_name', 'user_username', 'user_full_name']

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None

    def get_user_full_name(self, obj):
        if obj.user:
            full_name = obj.user.get_full_name()
            return full_name if full_name.strip() else obj.user.username
        return None

    def validate_employee_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Employee code is required.")
        return value.strip().upper()

    def validate(self, attrs):
        instance = self.instance
        company = attrs.get('company') or (instance.company if instance else None)
        employee_code = attrs.get('employee_code') or (instance.employee_code if instance else None)
        department = attrs.get('department') or (instance.department if instance else None)

        if company and employee_code:
            qs = Employee.objects.filter(company=company, employee_code=employee_code)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "employee_code": "An employee with this employee code already exists in this company."
                })

        if department and company:
            if department.company_id != company.id:
                raise serializers.ValidationError({
                    "department": "The selected department does not belong to the employee's company."
                })

        designation = attrs.get('designation') or (instance.designation if instance else None)
        if designation and company:
            if designation.company_id != company.id:
                raise serializers.ValidationError({
                    "designation": "The selected designation does not belong to the employee's company."
                })

        return attrs
