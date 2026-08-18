from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
import random
import string
from company.models import User, UserStatus, Role, Company, Department, Designation, Employee
from company.serializers.company import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    permissions = serializers.SerializerMethodField()

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
        ]
        read_only_fields = ["id", "created_at", "updated_at", "role_name", "last_login_at", "permissions"]

    def get_permissions(self, obj):
        return obj.get_all_permissions()

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
