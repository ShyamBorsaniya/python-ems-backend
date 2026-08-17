from rest_framework import serializers
from company.models import Company, Department, Designation


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'code',
            'email',
            'phone',
            'website',
            'address',
            'city',
            'state',
            'country',
            'logo',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Company code is required.")
        return value.strip().upper()


class DesignationPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentPublicSerializer(serializers.ModelSerializer):
    designations = DesignationPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_active',
            'created_at',
            'updated_at',
            'designations',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyPublicListSerializer(serializers.ModelSerializer):
    departments = DepartmentPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'code',
            'email',
            'phone',
            'website',
            'address',
            'city',
            'state',
            'country',
            'logo',
            'is_active',
            'created_at',
            'updated_at',
            'departments',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

