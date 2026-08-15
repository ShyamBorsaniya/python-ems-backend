from rest_framework import serializers
from company.models import Designation, DesignationPermissionSet
from company.serializers.department import DepartmentSerializer
from company.serializers.permission_set import PermissionSetSerializer


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


class DesignationPermissionSetSerializer(serializers.ModelSerializer):
    designation_name = serializers.ReadOnlyField(source='designation.name')
    permission_set_name = serializers.ReadOnlyField(source='permission_set.name')
    permission_set_code = serializers.ReadOnlyField(source='permission_set.code')

    class Meta:
        model = DesignationPermissionSet
        fields = [
            'id',
            'designation',
            'designation_name',
            'permission_set',
            'permission_set_name',
            'permission_set_code',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.designation:
            representation['designation'] = DesignationSerializer(instance.designation, context=self.context).data
        if instance.permission_set:
            representation['permission_set'] = PermissionSetSerializer(instance.permission_set, context=self.context).data
        return representation

    def validate(self, attrs):
        designation = attrs.get('designation', getattr(self.instance, 'designation', None))
        permission_set = attrs.get('permission_set', getattr(self.instance, 'permission_set', None))

        if not designation and not self.instance:
            raise serializers.ValidationError({"designation": "Designation is required."})

        if not permission_set and not self.instance:
            raise serializers.ValidationError({"permission_set": "Permission set is required."})

        if designation and permission_set:
            qs = DesignationPermissionSet.objects.filter(designation=designation, permission_set=permission_set)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "permission_set": "This permission set is already assigned to this designation."
                })

        return attrs
