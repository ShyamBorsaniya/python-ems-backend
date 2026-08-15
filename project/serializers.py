from rest_framework import serializers
from .models import Project, ProjectStatus, ProjectPriority, ProjectMember
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


class ProjectMemberSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    project_code = serializers.ReadOnlyField(source='project.code')
    employee_first_name = serializers.ReadOnlyField(source='employee.first_name')
    employee_last_name = serializers.ReadOnlyField(source='employee.last_name')
    employee_email = serializers.ReadOnlyField(source='employee.work_email')

    class Meta:
        model = ProjectMember
        fields = [
            'id',
            'project',
            'project_name',
            'project_code',
            'employee',
            'employee_first_name',
            'employee_last_name',
            'employee_email',
            'role_in_project',
            'assigned_at',
            'removed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'project_name',
            'project_code',
            'employee_first_name',
            'employee_last_name',
            'employee_email',
        ]

    def validate(self, attrs):
        project = attrs.get('project', getattr(self.instance, 'project', None))
        employee = attrs.get('employee', getattr(self.instance, 'employee', None))

        if not project and not self.instance:
            raise serializers.ValidationError({"project": "Project is required."})

        if not employee and not self.instance:
            raise serializers.ValidationError({"employee": "Employee is required."})

        if project and employee:
            qs = ProjectMember.objects.filter(project=project, employee=employee)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "employee": "This employee is already a member of this project."
                })

        assigned_at = attrs.get('assigned_at', getattr(self.instance, 'assigned_at', None))
        removed_at = attrs.get('removed_at', getattr(self.instance, 'removed_at', None))
        if assigned_at and removed_at and assigned_at > removed_at:
            raise serializers.ValidationError({"removed_at": "Removal date must be after or equal to assignment date."})

        return attrs


