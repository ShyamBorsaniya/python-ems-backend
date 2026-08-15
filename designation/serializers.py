from rest_framework import serializers
from .models import Designation
from department.serializers import DepartmentSerializer


class DesignationSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = Designation
        fields = [
            'id',
            'company',
            'company_name',
            'department',
            'name',
            'code',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.department:
            representation['department'] = DepartmentSerializer(instance.department).data
        else:
            representation['department'] = None
        return representation

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Designation name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Designation code is required.")
        return value.strip().upper()
