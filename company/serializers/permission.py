from rest_framework import serializers
from company.models import Permission
from company.serializers.company import CompanySerializer
from company.serializers.module import ModuleSerializer


class PermissionSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    module_name = serializers.ReadOnlyField(source='module.name')
    module_code = serializers.ReadOnlyField(source='module.code')

    class Meta:
        model = Permission
        fields = [
            'id',
            'company',
            'company_name',
            'module',
            'module_name',
            'module_code',
            'name',
            'display_name',
            'code',
            'action',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company:
            representation['company'] = CompanySerializer(instance.company).data
        else:
            representation['company'] = None
        if instance.module:
            representation['module'] = ModuleSerializer(instance.module).data
        else:
            representation['module'] = None
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

    def validate_action(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Action is required.")
        return value.strip()

    def validate(self, attrs):
        module = attrs.get('module', getattr(self.instance, 'module', None))
        code = attrs.get('code', getattr(self.instance, 'code', None))

        if not module and not self.instance:
            raise serializers.ValidationError({"module": "Module is required."})

        if module and code:
            qs = Permission.objects.filter(module=module, code=code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"code": "A permission with this code already exists within this module."})

        return attrs
