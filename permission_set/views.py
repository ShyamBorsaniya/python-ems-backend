from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from .models import PermissionSet, PermissionSetPermission
from .serializers import PermissionSetSerializer, PermissionSetPermissionSerializer


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


class PermissionSetListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSetSerializer
    page_size = 10

    def get(self, request):
        permission_sets = PermissionSet.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        code_param = request.query_params.get("code", None)

        if search_query:
            permission_sets = permission_sets.filter(
                Q(name__icontains=search_query) |
                Q(display_name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if company_param is not None:
            if company_param.lower() in ["null", "none"]:
                permission_sets = permission_sets.filter(company__isnull=True)
            else:
                permission_sets = permission_sets.filter(company_id=company_param)

        if code_param:
            permission_sets = permission_sets.filter(code__iexact=code_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(permission_sets, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = PermissionSetSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission sets retrieved successfully",
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
        serializer = PermissionSetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Permission set created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set creation failed",
            errors=serializer.errors
        )


class PermissionSetDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSetSerializer

    def get_object(self, pk):
        return get_object_or_404(PermissionSet, pk=pk)

    def get(self, request, pk):
        permission_set = self.get_object(pk)
        serializer = PermissionSetSerializer(permission_set, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission set details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        permission_set = self.get_object(pk)
        serializer = PermissionSetSerializer(permission_set, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        permission_set = self.get_object(pk)
        serializer = PermissionSetSerializer(permission_set, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        permission_set = self.get_object(pk)
        permission_set.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission set deleted successfully"
        )


class PermissionSetPermissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSetPermissionSerializer
    page_size = 10

    def get(self, request):
        ps_permissions = PermissionSetPermission.objects.all()
        search_query = request.query_params.get("search", None)
        permission_set_param = request.query_params.get("permission_set", None)
        permission_param = request.query_params.get("permission", None)

        if search_query:
            ps_permissions = ps_permissions.filter(
                Q(permission_set__name__icontains=search_query) |
                Q(permission_set__code__icontains=search_query) |
                Q(permission__name__icontains=search_query) |
                Q(permission__code__icontains=search_query)
            )

        if permission_set_param:
            ps_permissions = ps_permissions.filter(permission_set_id=permission_set_param)

        if permission_param:
            ps_permissions = ps_permissions.filter(permission_id=permission_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(ps_permissions, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = PermissionSetPermissionSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission set permissions retrieved successfully",
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
        serializer = PermissionSetPermissionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Permission set permission mapping created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set permission mapping creation failed",
            errors=serializer.errors
        )


class PermissionSetPermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PermissionSetPermissionSerializer

    def get_object(self, pk):
        return get_object_or_404(PermissionSetPermission, pk=pk)

    def get(self, request, pk):
        ps_permission = self.get_object(pk)
        serializer = PermissionSetPermissionSerializer(ps_permission, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission set permission mapping details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        ps_permission = self.get_object(pk)
        serializer = PermissionSetPermissionSerializer(ps_permission, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission set permission mapping updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set permission mapping update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        ps_permission = self.get_object(pk)
        serializer = PermissionSetPermissionSerializer(ps_permission, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Permission set permission mapping updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Permission set permission mapping update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        ps_permission = self.get_object(pk)
        ps_permission.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Permission set permission mapping deleted successfully"
        )

