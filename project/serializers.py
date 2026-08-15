from rest_framework import serializers
from .models import Project, ProjectStatus, ProjectPriority
from company.models import Company


class ProjectSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = Project
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'code',
            'description',
            'start_date',
            'end_date',
            'status',
            'priority',
            'budget',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'company_name',
        ]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Project name is required.")
        return value.strip()

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Project code is required.")
        cleaned_code = value.strip().upper()
        instance = self.instance
        if Project.objects.filter(code=cleaned_code).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("A project with this project code already exists.")
        return cleaned_code

    def validate(self, attrs):
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        end_date = attrs.get('end_date', self.instance.end_date if self.instance else None)
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be after or equal to start date."})
        return attrs

