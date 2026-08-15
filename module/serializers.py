from rest_framework import serializers
from .models import Module
from company.models import Company
from company.serializers import CompanySerializer


class ModuleSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = Module
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'display_name',
            'code',
            'description',
            'is_active',
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
        return representation

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Module name is required.")
        return value.strip()

    def validate_display_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Display name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Module code is required.")
        return value.strip().upper()

    def validate(self, attrs):
        company = attrs.get('company', getattr(self.instance, 'company', None))
        code = attrs.get('code', getattr(self.instance, 'code', None))

        if code:
            qs = Module.objects.filter(company=company, code=code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"code": "A module with this code already exists for this company."})

        return attrs
