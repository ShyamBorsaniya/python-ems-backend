from rest_framework import serializers
from company.models import PermissionSet, PermissionSetPermission
from company.serializers.company import CompanySerializer
from company.serializers.permission import PermissionSerializer


class PermissionSetSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = PermissionSet
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'display_name',
            'code',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        validators = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company:
            representation['company'] = CompanySerializer(instance.company).data
        else:
            representation['company'] = None
        return representation

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()

    def validate_display_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Display name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code is required.")
        return value.strip()

    def validate(self, attrs):
        company = attrs.get('company', getattr(self.instance, 'company', None))
        code = attrs.get('code', getattr(self.instance, 'code', None))

        if code:
            qs = PermissionSet.objects.filter(company=company, code=code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "code": "A permission set with this code already exists for this company."
                })

        return attrs


class PermissionSetPermissionSerializer(serializers.ModelSerializer):
    permission_set_name = serializers.ReadOnlyField(source='permission_set.name')
    permission_set_code = serializers.ReadOnlyField(source='permission_set.code')
    permission_name = serializers.ReadOnlyField(source='permission.name')
    permission_code = serializers.ReadOnlyField(source='permission.code')

    class Meta:
        model = PermissionSetPermission
        fields = [
            'id',
            'permission_set',
            'permission_set_name',
            'permission_set_code',
            'permission',
            'permission_name',
            'permission_code',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        validators = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.permission_set:
            representation['permission_set'] = PermissionSetSerializer(instance.permission_set, context=self.context).data
        if instance.permission:
            representation['permission'] = PermissionSerializer(instance.permission, context=self.context).data
        return representation

    def validate(self, attrs):
        permission_set = attrs.get('permission_set', getattr(self.instance, 'permission_set', None))
        permission = attrs.get('permission', getattr(self.instance, 'permission', None))

        if not permission_set and not self.instance:
            raise serializers.ValidationError({"permission_set": "Permission set is required."})

        if not permission and not self.instance:
            raise serializers.ValidationError({"permission": "Permission is required."})

        if permission_set and permission:
            qs = PermissionSetPermission.objects.filter(permission_set=permission_set, permission=permission)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "permission": "This permission is already assigned to this permission set."
                })

        return attrs
