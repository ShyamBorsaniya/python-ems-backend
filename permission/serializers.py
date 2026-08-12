from rest_framework import serializers
from .models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'resource',
            'action',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_resource(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Resource is required.")
        return value.strip()

    def validate_action(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Action is required.")
        return value.strip()

    def create(self, validated_data):
        if not validated_data.get('name'):
            resource = validated_data.get('resource', '').strip().lower()
            action = validated_data.get('action', '').strip().lower()
            validated_data['name'] = f"{resource}.{action}"
        return super().create(validated_data)
