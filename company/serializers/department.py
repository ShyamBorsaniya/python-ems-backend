from rest_framework import serializers
from company.models import Department, DepartmentPermissionSet, Company, Designation
from company.serializers.permission_set import PermissionSetSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

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
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Department code is required.")
        return value.strip().upper()


class DepartmentPermissionSetSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    permission_set_name = serializers.ReadOnlyField(source='permission_set.name')
    permission_set_code = serializers.ReadOnlyField(source='permission_set.code')

    class Meta:
        model = DepartmentPermissionSet
        fields = [
            'id',
            'department',
            'department_name',
            'permission_set',
            'permission_set_name',
            'permission_set_code',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.department:
            representation['department'] = DepartmentSerializer(instance.department, context=self.context).data
        if instance.permission_set:
            representation['permission_set'] = PermissionSetSerializer(instance.permission_set, context=self.context).data
        return representation

    def validate(self, attrs):
        department = attrs.get('department', getattr(self.instance, 'department', None))
        permission_set = attrs.get('permission_set', getattr(self.instance, 'permission_set', None))

        if not department and not self.instance:
            raise serializers.ValidationError({"department": "Department is required."})

        if not permission_set and not self.instance:
            raise serializers.ValidationError({"permission_set": "Permission set is required."})

        if department and permission_set:
            qs = DepartmentPermissionSet.objects.filter(department=department, permission_set=permission_set)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "permission_set": "This permission set is already assigned to this department."
                })

        return attrs


class DesignationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name', 'code', 'is_active']


class DepartmentDesignationListSerializer(serializers.ModelSerializer):
    designations = DesignationSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'is_active',
            'designations'
        ]

