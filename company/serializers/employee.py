from rest_framework import serializers
from company.models import Employee, EmploymentType, EmploymentStatus, Gender, User, Company, Department, Designation
from company.serializers.department import DepartmentSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_full_name = serializers.SerializerMethodField()
    company_name = serializers.ReadOnlyField(source='company.name')
    department_name = serializers.ReadOnlyField(source='department.name')
    designation_name = serializers.ReadOnlyField(source='designation.name')

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'user_username',
            'user_email',
            'user_full_name',
            'company',
            'company_name',
            'code',
            'department',
            'department_name',
            'designation',
            'designation_name',
            'joining_date',
            'employment_type',
            'employment_status',
            'date_of_birth',
            'gender',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
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
        if instance.designation:
            from company.serializers.designation import DesignationSerializer
            representation['designation'] = DesignationSerializer(instance.designation, context=self.context).data
        else:
            representation['designation'] = None
        return representation

    def get_user_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return ""

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Employee code is required.")
        return value.strip().upper()

    def validate(self, attrs):
        company = attrs.get('company', getattr(self.instance, 'company', None))
        department = attrs.get('department', getattr(self.instance, 'department', None))
        designation = attrs.get('designation', getattr(self.instance, 'designation', None))
        code = attrs.get('code', getattr(self.instance, 'code', None))
        user = attrs.get('user', getattr(self.instance, 'user', None))

        if department and company and department.company_id != company.id:
            raise serializers.ValidationError({"department": "Department does not belong to the selected company."})

        if designation and company and designation.company_id != company.id:
            raise serializers.ValidationError({"designation": "Designation does not belong to the selected company."})

        if company and code:
            qs = Employee.objects.filter(company=company, code=code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"code": "An employee with this code already exists in this company."})

        if user:
            qs = Employee.objects.filter(user=user)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"user": "This user already has an employee profile."})

        return attrs
