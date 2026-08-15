from rest_framework import serializers
from django.contrib.auth import authenticate
from company.models import User, UserStatus, Role, Company
from company.serializers.company import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')

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
        ]
        read_only_fields = ["id", "created_at", "updated_at", "role_name", "last_login_at"]

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
        ]
        extra_kwargs = {
            "status": {"required": False, "default": UserStatus.ACTIVE}
        }

    def create(self, validated_data):
        role = validated_data.pop("role")
        company = validated_data.pop("company")
        status_val = validated_data.pop("status", None)
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
        user = User.objects.create_user(**create_kwargs)
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
            raise serializers.ValidationError("your account has been inactivated please contact to admin")

        if user.status == UserStatus.INACTIVE:
            raise serializers.ValidationError("your account has been inactivated please contact to admin")

        if user.status == UserStatus.LOCKED:
            raise serializers.ValidationError("your account has been locked, contact to admin for further query")

        attrs["user"] = user
        return attrs
