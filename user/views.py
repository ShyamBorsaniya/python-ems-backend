from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def standard_response(status_code, message, data=None, errors=None):
    payload = {
        "status_code": status_code,
        "success": status.is_success(status_code),
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="User registered successfully",
                data={
                    "user": UserSerializer(user).data
                }
            )

        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User registration failed",
            errors=serializer.errors
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Login successful",
                data={
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "user": UserSerializer(user).data
                }
            )

        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Login failed",
            errors=serializer.errors
        )


from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.all().select_related('role', 'company').order_by('-date_joined')
        search_query = request.query_params.get("search", None)
        role_param = request.query_params.get("role", None)
        company_param = request.query_params.get("company", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            from django.db.models import Q
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        if role_param:
            users = users.filter(role_id=role_param)

        if company_param:
            users = users.filter(company_id=company_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            users = users.filter(is_active=is_active)

        serializer = UserSerializer(users, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Users retrieved successfully",
            data=serializer.data
        )


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="User details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="User updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="User updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.is_active = False
        user.save()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="User deactivated successfully",
            data=UserSerializer(user, context={'request': request}).data
        )
