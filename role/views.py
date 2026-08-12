from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, ProtectedError
from django.core.paginator import Paginator

from .models import Role, RolePermission
from .serializers import RoleSerializer, RolePermissionSerializer


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


class RoleListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = RoleSerializer
    page_size = 10

    def get(self, request):
        roles = Role.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)

        if search_query:
            roles = roles.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            roles = roles.filter(company=request.user.company)
        elif company_param:
            roles = roles.filter(company_id=company_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(roles, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = RoleSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Roles retrieved successfully",
            data={
                "results": serializer.data,
                "pagination": {
                    "page": page.number,
                    "page_size": page_size,
                    "total_items": paginator.count,
                    "total_pages": paginator.num_pages,
                    "next_page": page.next_page_number() if page.has_next() else None,
                    "previous_page": page.previous_page_number() if page.has_previous() else None,
                },
            }
        )

    def post(self, request):
        serializer = RoleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Role created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role creation failed",
            errors=serializer.errors
        )


class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = RoleSerializer

    def get_object(self, pk):
        return get_object_or_404(Role, pk=pk)

    def get(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Role details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Role updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Role updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        role = self.get_object(pk)
        try:
            role.delete()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Role deleted successfully"
            )
        except ProtectedError:
            return standard_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Cannot delete role because it is assigned to users."
            )


class RolePermissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = RolePermissionSerializer
    page_size = 10

    def get(self, request):
        role_permissions = RolePermission.objects.select_related('role', 'permission').all()
        role_param = request.query_params.get("role", None)
        permission_param = request.query_params.get("permission", None)
        search_query = request.query_params.get("search", None)

        if role_param:
            role_permissions = role_permissions.filter(role_id=role_param)

        if permission_param:
            role_permissions = role_permissions.filter(permission_id=permission_param)

        if search_query:
            role_permissions = role_permissions.filter(
                Q(role__name__icontains=search_query) |
                Q(permission__name__icontains=search_query) |
                Q(permission__resource__icontains=search_query) |
                Q(permission__action__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            role_permissions = role_permissions.filter(
                Q(role__company=request.user.company) | Q(role__company__isnull=True)
            )

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(role_permissions, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = RolePermissionSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Role permissions retrieved successfully",
            data={
                "results": serializer.data,
                "pagination": {
                    "page": page.number,
                    "page_size": page_size,
                    "total_items": paginator.count,
                    "total_pages": paginator.num_pages,
                    "next_page": page.next_page_number() if page.has_next() else None,
                    "previous_page": page.previous_page_number() if page.has_previous() else None,
                },
            }
        )

    def post(self, request):
        serializer = RolePermissionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Role permission assigned successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role permission assignment failed",
            errors=serializer.errors
        )


class RolePermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = RolePermissionSerializer

    def get_object(self, pk):
        return get_object_or_404(RolePermission, pk=pk)

    def get(self, request, pk):
        role_permission = self.get_object(pk)
        serializer = RolePermissionSerializer(role_permission, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Role permission details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        role_permission = self.get_object(pk)
        serializer = RolePermissionSerializer(role_permission, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Role permission updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role permission update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        role_permission = self.get_object(pk)
        serializer = RolePermissionSerializer(role_permission, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Role permission updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Role permission update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        role_permission = self.get_object(pk)
        role_permission.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Role permission deleted successfully"
        )

