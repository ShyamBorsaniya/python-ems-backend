from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Role, RolePermission
from company.models import Company


class RoleSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = Role
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'code',
            'description',
            'is_system_role',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Role name is required.")
        return value.strip()


class RolePermissionSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    permission_name = serializers.ReadOnlyField(source='permission.name')

    class Meta:
        model = RolePermission
        fields = [
            'id',
            'role',
            'role_name',
            'permission',
            'permission_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = [
            UniqueTogetherValidator(
                queryset=RolePermission.objects.all(),
                fields=['role', 'permission'],
                message="This permission is already assigned to this role."
            )
        ]


