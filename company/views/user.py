from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from company.models import User, UserStatus
from company.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from company.views.company import standard_response


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            if user.status == UserStatus.INACTIVE:
                return standard_response(
                    status_code=status.HTTP_201_CREATED,
                    message="you are registered successfully but your account is inactive, please wait until admin can activate it"
                )

            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="User registered successfully",
                data={
                    "user": UserSerializer(user, context={'request': request}).data
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
                    "user": UserSerializer(user, context={'request': request}).data
                }
            )

        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Login failed",
            errors=serializer.errors
        )


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer
    page_size = 5

    def get(self, request):
        users = User.objects.all().select_related('role', 'company').order_by('-date_joined')
        if not getattr(request.user, 'is_superuser', False):
            users = users.filter(is_superuser=False)

        search_query = request.query_params.get("search", None)
        role_param = request.query_params.get("role", None)
        company_param = request.query_params.get("company", None)
        status_param = request.query_params.get("status", None)
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

        if status_param:
            users = users.filter(status=status_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            users = users.filter(is_active=is_active)

        paginator = Paginator(users, self.page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = UserSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Users retrieved successfully",
            data={
                "results": serializer.data,
                "pagination": {
                    "page": page.number,
                    "page_size": self.page_size,
                    "total_items": paginator.count,
                    "total_pages": paginator.num_pages,
                    "next_page": page.next_page_number() if page.has_next() else None,
                    "previous_page": page.previous_page_number() if page.has_previous() else None,
                },
            }
        )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="User created successfully",
                data={"user": UserSerializer(user, context={'request': request}).data}
            )

        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="User creation failed",
            errors=serializer.errors
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


class UserRestoreView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="User restored successfully",
            data=UserSerializer(user, context={'request': request}).data
        )


class PendingUserListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer
    page_size = 5

    def get(self, request):
        users = User.objects.filter(status=UserStatus.INACTIVE).select_related('role', 'company').order_by('-date_joined')
        if not getattr(request.user, 'is_superuser', False):
            users = users.filter(is_superuser=False)

        if request.user.company:
            users = users.filter(company=request.user.company)

        company_param = request.query_params.get("company", None)
        if company_param:
            users = users.filter(company_id=company_param)

        search_query = request.query_params.get("search", None)
        if search_query:
            from django.db.models import Q
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        paginator = Paginator(users, self.page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = UserSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Pending users retrieved successfully",
            data={
                "results": serializer.data,
                "pagination": {
                    "page": page.number,
                    "page_size": self.page_size,
                    "total_items": paginator.count,
                    "total_pages": paginator.num_pages,
                    "next_page": page.next_page_number() if page.has_next() else None,
                    "previous_page": page.previous_page_number() if page.has_previous() else None,
                },
            }
        )


class UserApproveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.status = UserStatus.ACTIVE
        user.save()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="User approved successfully",
            data=UserSerializer(user, context={'request': request}).data
        )


class UserRejectView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = UserSerializer

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.status = UserStatus.LOCKED
        user.save()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="User rejected successfully",
            data=UserSerializer(user, context={'request': request}).data
        )
