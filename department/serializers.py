from rest_framework import serializers
from .models import Department
from company.models import Company


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'code',
            'description',
            'is_active',
            'employee_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count']

    def get_employee_count(self, obj):
        return obj.employees.count()

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department code is required.")
        return value.strip().upper()
