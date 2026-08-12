from rest_framework import serializers
from .models import Project, ProjectStatus, ProjectPriority, ProjectMember
from company.models import Company
from department.models import Department
from employee.models import Employee


class ProjectSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    department_name = serializers.SerializerMethodField()
    project_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'company',
            'company_name',
            'department',
            'department_name',
            'name',
            'code',
            'description',
            'start_date',
            'end_date',
            'status',
            'priority',
            'project_manager',
            'project_manager_name',
            'budget',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'company_name',
            'department_name',
            'project_manager_name',
        ]

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_project_manager_name(self, obj):
        if obj.project_manager:
            if obj.project_manager.user and obj.project_manager.user.get_full_name().strip():
                return f"{obj.project_manager.employee_code} - {obj.project_manager.user.get_full_name()}"
            return f"{obj.project_manager.employee_code} - {obj.project_manager.designation}"
        return None

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


class ProjectMemberSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMember
        fields = [
            'id',
            'project',
            'project_name',
            'employee',
            'employee_code',
            'employee_name',
            'role',
            'joined_at',
            'left_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'project_name',
            'employee_code',
            'employee_name',
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            if obj.employee.user and obj.employee.user.get_full_name().strip():
                return f"{obj.employee.employee_code} - {obj.employee.user.get_full_name()}"
            return f"{obj.employee.employee_code} - {obj.employee.designation}"
        return None

    def validate(self, attrs):
        joined_at = attrs.get('joined_at', self.instance.joined_at if self.instance else None)
        left_at = attrs.get('left_at', self.instance.left_at if self.instance else None)
        if joined_at and left_at and joined_at > left_at:
            raise serializers.ValidationError({"left_at": "Left date must be after or equal to joined date."})
        return attrs

