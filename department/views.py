from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Department
from .serializers import DepartmentSerializer


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


class DepartmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentSerializer

    def get(self, request):
        departments = Department.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            departments = departments.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        if company_param:
            departments = departments.filter(company_id=company_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            departments = departments.filter(is_active=is_active)

        serializer = DepartmentSerializer(departments, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Departments retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Department created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department creation failed",
            errors=serializer.errors
        )


class DepartmentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentSerializer

    def get_object(self, pk):
        return get_object_or_404(Department, pk=pk)

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Department updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Department updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        department = self.get_object(pk)
        department.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department deleted successfully"
        )
