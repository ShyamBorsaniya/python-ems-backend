from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Permission
from .serializers import PermissionSerializer


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


class PermissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSerializer
    page_size = 10

    def get(self, request):
        permissions = Permission.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        module_param = request.query_params.get("module", None)
        action_param = request.query_params.get("action", None)
        code_param = request.query_params.get("code", None)

        if search_query:
            permissions = permissions.filter(
                Q(name__icontains=search_query) |
                Q(display_name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(action__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(module__name__icontains=search_query)
            )

        if company_param:
            permissions = permissions.filter(company_id=company_param)

        if module_param:
            permissions = permissions.filter(module_id=module_param)

        if action_param:
            permissions = permissions.filter(action__iexact=action_param)

        if code_param:
            permissions = permissions.filter(code__iexact=code_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(permissions, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = PermissionSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permissions retrieved successfully",
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
        serializer = PermissionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Permission created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission creation failed",
            errors=serializer.errors
        )


class PermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSerializer

    def get_object(self, pk):
        return get_object_or_404(Permission, pk=pk)

    def get(self, request, pk):
        permission = self.get_object(pk)
        serializer = PermissionSerializer(permission, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        permission = self.get_object(pk)
        serializer = PermissionSerializer(permission, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        permission = self.get_object(pk)
        serializer = PermissionSerializer(permission, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        permission = self.get_object(pk)
        permission.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission deleted successfully"
        )
