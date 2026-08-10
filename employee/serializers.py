from rest_framework import serializers
from .models import Employee, EmploymentType, EmployeeStatus, Gender
from company.models import Company
from department.models import Department
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    department_name = serializers.SerializerMethodField()
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
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name', 'department_name', 'user_username', 'user_full_name']

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
        cleaned_value = value.strip().upper()
        # Check uniqueness during creation or update
        instance = self.instance
        if Employee.objects.filter(employee_code=cleaned_value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("An employee with this employee code already exists.")
        return cleaned_value
