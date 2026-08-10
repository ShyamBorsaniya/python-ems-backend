from rest_framework import serializers
from .models import Department
from company.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'description',
            'manager',
            'manager_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_manager_name(self, obj):
        if obj.manager:
            full_name = obj.manager.get_full_name()
            return full_name if full_name.strip() else obj.manager.username
        return None

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department name is required.")
        return value.strip()
