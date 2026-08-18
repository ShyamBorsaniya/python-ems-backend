from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
import random
import string
from company.models import User, UserStatus, Role, Company, Department, Designation, Employee, EmploymentType, EmploymentStatus, Gender
from company.serializers.company import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    permissions = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    # designation = serializers.SerializerMethodField()
    # department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile_photo_url",
            "company",
            "role",
            "role_name",
            "status",
            "is_active",
            "last_login_at",
            "created_at",
            "updated_at",
            "permissions",
            "employee",
            # "designation",
            # "department",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "role_name", "last_login_at", "permissions"]

    def get_permissions(self, obj):
        return obj.get_all_permissions()

    def get_employee(self, obj):
        try:
            employee = obj.employee
        except (AttributeError, Employee.DoesNotExist):
            return None
        from company.serializers.employee import EmployeeSerializer
        return EmployeeSerializer(employee, context=self.context).data

    # def get_designation(self, obj):
    #     try:
    #         employee = obj.employee
    #     except (AttributeError, Employee.DoesNotExist):
    #         return None
    #     if employee and employee.designation:
    #         from company.serializers.designation import DesignationSerializer
    #         return DesignationSerializer(employee.designation, context=self.context).data
    #     return None

    # def get_department(self, obj):
    #     try:
    #         employee = obj.employee
    #     except (AttributeError, Employee.DoesNotExist):
    #         return None
    #     if employee and employee.department:
    #         from company.serializers.department import DepartmentSerializer
    #         return DepartmentSerializer(employee.department, context=self.context).data
    #     return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company:
            representation["company"] = CompanySerializer(instance.company, context=self.context).data
        else:
            representation["company"] = None
        return representation


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True,
        allow_null=False
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True,
        allow_null=False
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "company",
            "role",
            "status",
            "department",
            "designation",
        ]
        extra_kwargs = {
            "status": {"required": False, "default": UserStatus.APPROVE}
        }

    def validate(self, attrs):
        company = attrs.get('company')
        department = attrs.get('department')
        designation = attrs.get('designation')
        errors = {}

        if department and company and department.company_id != company.id:
            errors["department"] = "Department does not belong to the selected company."

        if designation and company and designation.company_id != company.id:
            errors["designation"] = "Designation does not belong to the selected company."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        role = validated_data.pop("role")
        company = validated_data.pop("company")
        status_val = validated_data.pop("status", None)
        department = validated_data.pop("department", None)
        designation = validated_data.pop("designation", None)

        create_kwargs = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "password": validated_data["password"],
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
            "role": role,
            "company": company,
        }
        if status_val:
            create_kwargs["status"] = status_val

        with transaction.atomic():
            user = User.objects.create_user(**create_kwargs)

            # Auto Generate employee code in this format:
            # EMP-{Company code}-{Year}-{random 4 digits include alphabet and numbers}
            company_code = company.code.strip().upper() if company.code else "COMP"
            year = timezone.now().year

            while True:
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                code = f"EMP-{company_code}-{year}-{random_suffix}"
                if not Employee.objects.filter(company=company, code=code).exists():
                    break

            Employee.objects.create(
                user=user,
                company=company,
                code=code,
                department=department,
                designation=designation,
                joining_date=timezone.now().date()
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        user = None
        if "@" in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                pass

        if not user:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                pass

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive, please contact to admin for further query")

        if user.status == UserStatus.PENDING:
            raise serializers.ValidationError("Your account is pending, please contact to admin for further query")

        if user.status == UserStatus.REJECTED:
            raise serializers.ValidationError("Your account has been rejected, please contact to admin for further query")

        attrs["user"] = user
        return attrs


class EmployeeOnboardSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=True
    )
    employment_type = serializers.ChoiceField(
        choices=EmploymentType.choices,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    employment_status = serializers.ChoiceField(
        choices=EmploymentStatus.choices,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    gender = serializers.ChoiceField(
        choices=Gender.choices,
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Employee
        fields = [
            "code",
            "department",
            "designation",
            "joining_date",
            "employment_type",
            "employment_status",
            "date_of_birth",
            "gender",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]
        extra_kwargs = {
            "joining_date": {"required": False, "allow_null": True},
            "code": {"required": False, "allow_null": True, "allow_blank": True},
        }


class UserOnboardSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True,
        allow_null=False
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True,
        allow_null=False
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )
    is_active = serializers.BooleanField(required=False, default=True)
    employee_details = EmployeeOnboardSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "profile_photo_url",
            "is_active",
            "company",
            "role",
            "status",
            "employee_details",
        ]
        extra_kwargs = {
            "status": {"required": False, "default": UserStatus.APPROVE}
        }

    def validate(self, attrs):
        if not self.instance and not attrs.get("password"):
            raise serializers.ValidationError({"password": "This field is required for user onboarding."})

        company = attrs.get("company", getattr(self.instance, "company", None))
        employee = getattr(self.instance, "employee", None) if self.instance else None

        employee_details = attrs.get("employee_details", {}) or {}

        department = employee_details.get("department")
        if department is None and employee:
            department = employee.department

        designation = employee_details.get("designation")
        if designation is None and employee:
            designation = employee.designation

        code = employee_details.get("code")
        if code is None and employee:
            code = employee.code

        errors = {}

        if department and company and department.company_id != company.id:
            errors["department"] = "Department does not belong to the selected company."

        if designation and company and designation.company_id != company.id:
            errors["designation"] = "Designation does not belong to the selected company."

        if company and code:
            code_clean = code.strip().upper()
            qs = Employee.objects.filter(company=company, code=code_clean)
            if employee:
                qs = qs.exclude(pk=employee.pk)
            if qs.exists():
                errors["code"] = "An employee with this code already exists in this company."

        if errors:
            raise serializers.ValidationError({"employee_details": errors})

        return attrs

    def create(self, validated_data):
        employee_data = validated_data.pop("employee_details", {}) or {}

        role = validated_data.pop("role")
        company = validated_data.pop("company")
        status_val = validated_data.pop("status", None)

        create_kwargs = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "password": validated_data["password"],
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
            "phone": validated_data.get("phone", None),
            "profile_photo_url": validated_data.get("profile_photo_url", None),
            "role": role,
            "company": company,
        }
        if status_val:
            create_kwargs["status"] = status_val

        with transaction.atomic():
            user = User.objects.create_user(**create_kwargs)

            code = employee_data.get("code")
            if code:
                code = code.strip().upper()
            else:
                company_code = company.code.strip().upper() if company.code else "COMP"
                year = timezone.now().year
                while True:
                    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    code = f"EMP-{company_code}-{year}-{random_suffix}"
                    if not Employee.objects.filter(company=company, code=code).exists():
                        break

            joining_date = employee_data.get("joining_date") or timezone.now().date()

            employee = Employee.objects.create(
                user=user,
                company=company,
                code=code,
                department=employee_data.get("department"),
                designation=employee_data.get("designation"),
                joining_date=joining_date,
                employment_type=employee_data.get("employment_type"),
                employment_status=employee_data.get("employment_status") or EmploymentStatus.ACTIVE,
                date_of_birth=employee_data.get("date_of_birth"),
                gender=employee_data.get("gender"),
                address=employee_data.get("address"),
                emergency_contact_name=employee_data.get("emergency_contact_name"),
                emergency_contact_phone=employee_data.get("emergency_contact_phone"),
            )
            user.employee = employee

        return user

    def update(self, instance, validated_data):
        employee_data = validated_data.pop("employee_details", None)

        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            instance.save()

            if employee_data is not None or "company" in validated_data:
                employee, created = Employee.objects.get_or_create(
                    user=instance,
                    defaults={
                        "company": instance.company,
                        "joining_date": timezone.now().date(),
                        "code": (employee_data or {}).get("code") or "TEMP-CODE"
                    }
                )

                if "company" in validated_data:
                    employee.company = validated_data["company"]

                if employee_data:
                    if "code" in employee_data and employee_data["code"]:
                        employee.code = employee_data["code"].strip().upper()
                    elif created and not employee_data.get("code"):
                        company_code = employee.company.code.strip().upper() if employee.company.code else "COMP"
                        year = timezone.now().year
                        while True:
                            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                            code = f"EMP-{company_code}-{year}-{random_suffix}"
                            if not Employee.objects.filter(company=employee.company, code=code).exists():
                                break
                        employee.code = code

                    if "department" in employee_data:
                        employee.department = employee_data["department"]
                    if "designation" in employee_data:
                        employee.designation = employee_data["designation"]
                    if "joining_date" in employee_data and employee_data["joining_date"]:
                        employee.joining_date = employee_data["joining_date"]
                    if "employment_type" in employee_data:
                        employee.employment_type = employee_data["employment_type"]
                    if "employment_status" in employee_data:
                        employee.employment_status = employee_data["employment_status"]
                    if "date_of_birth" in employee_data:
                        employee.date_of_birth = employee_data["date_of_birth"]
                    if "gender" in employee_data:
                        employee.gender = employee_data["gender"]
                    if "address" in employee_data:
                        employee.address = employee_data["address"]
                    if "emergency_contact_name" in employee_data:
                        employee.emergency_contact_name = employee_data["emergency_contact_name"]
                    if "emergency_contact_phone" in employee_data:
                        employee.emergency_contact_phone = employee_data["emergency_contact_phone"]

                employee.save()
                instance.employee = employee

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            employee = instance.employee
        except Employee.DoesNotExist:
            employee = None

        if employee:
            employee_serialized = EmployeeOnboardSerializer(employee).data
            employee_serialized["department_name"] = employee.department.name if employee.department else None
            employee_serialized["designation_name"] = employee.designation.name if employee.designation else None
            representation["employee_details"] = employee_serialized
        else:
            representation["employee_details"] = None

        if instance.company:
            representation["company"] = CompanySerializer(instance.company, context=self.context).data
            representation["company_name"] = instance.company.name
        else:
            representation["company"] = None
            representation["company_name"] = None

        if instance.role:
            representation["role_name"] = instance.role.name
        else:
            representation["role_name"] = None

        return representation

