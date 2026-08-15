from rest_framework import serializers
from company.models import Role, RolePermissionSet
from company.serializers.permission_set import PermissionSetSerializer


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


class RolePermissionSetSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    permission_set_name = serializers.ReadOnlyField(source='permission_set.name')
    permission_set_code = serializers.ReadOnlyField(source='permission_set.code')

    class Meta:
        model = RolePermissionSet
        fields = [
            'id',
            'role',
            'role_name',
            'permission_set',
            'permission_set_name',
            'permission_set_code',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.role:
            representation['role'] = RoleSerializer(instance.role, context=self.context).data
        if instance.permission_set:
            representation['permission_set'] = PermissionSetSerializer(instance.permission_set, context=self.context).data
        return representation

    def validate(self, attrs):
        role = attrs.get('role', getattr(self.instance, 'role', None))
        permission_set = attrs.get('permission_set', getattr(self.instance, 'permission_set', None))

        if not role and not self.instance:
            raise serializers.ValidationError({"role": "Role is required."})

        if not permission_set and not self.instance:
            raise serializers.ValidationError({"permission_set": "Permission set is required."})

        if role and permission_set:
            qs = RolePermissionSet.objects.filter(role=role, permission_set=permission_set)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "permission_set": "This permission set is already assigned to this role."
                })

        return attrs
