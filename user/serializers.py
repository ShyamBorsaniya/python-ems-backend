from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from role.models import Role
from company.models import Company


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    company_name = serializers.ReadOnlyField(source='company.name')

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile_image",
            "company",
            "company_name",
            "role",
            "role_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "role_name", "company_name"]


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
        ]

    def create(self, validated_data):
        role = validated_data.pop("role")
        company = validated_data.pop("company")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=role,
            company=company,
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
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs