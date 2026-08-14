from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Role, RolePermission


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'display_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

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


