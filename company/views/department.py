from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from company.models import Department, DepartmentPermissionSet
from company.serializers.department import DepartmentSerializer, DepartmentPermissionSetSerializer
from company.views.company import standard_response
from company.mixins import PermissionCheckMixin


class DepartmentListCreateView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentSerializer
    page_size = 10
    module_code = 'department_management'

    def get(self, request):
        perm_error = self.check_permission(request, action='view')
        if perm_error:
            return perm_error

        departments = Department.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            departments = departments.filter(
                Q(name__icontains=search_query) | Q(code__icontains=search_query) | Q(description__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            departments = departments.filter(company=request.user.company)
        elif company_param:
            departments = departments.filter(company_id=company_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            departments = departments.filter(is_active=is_active)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(departments, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = DepartmentSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Departments retrieved successfully",
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
        perm_error = self.check_permission(request, action='create')
        if perm_error:
            return perm_error

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


class DepartmentDetailView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentSerializer
    module_code = 'department_management'

    def get_object(self, pk):
        return get_object_or_404(Department, pk=pk)

    def get(self, request, pk):
        perm_error = self.check_permission(request, action='view')
        if perm_error:
            return perm_error

        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        perm_error = self.check_permission(request, action='edit')
        if perm_error:
            return perm_error

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
        perm_error = self.check_permission(request, action='edit')
        if perm_error:
            return perm_error

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
        perm_error = self.check_permission(request, action='delete')
        if perm_error:
            return perm_error

        department = self.get_object(pk)
        department.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department deleted successfully"
        )


class DepartmentPermissionSetListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentPermissionSetSerializer
    page_size = 10

    def get(self, request):
        dept_permission_sets = DepartmentPermissionSet.objects.all()
        search_query = request.query_params.get("search", None)
        department_param = request.query_params.get("department", None)
        permission_set_param = request.query_params.get("permission_set", None)

        if search_query:
            dept_permission_sets = dept_permission_sets.filter(
                Q(department__name__icontains=search_query) |
                Q(department__code__icontains=search_query) |
                Q(permission_set__name__icontains=search_query) |
                Q(permission_set__code__icontains=search_query)
            )

        if department_param:
            dept_permission_sets = dept_permission_sets.filter(department_id=department_param)

        if permission_set_param:
            dept_permission_sets = dept_permission_sets.filter(permission_set_id=permission_set_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(dept_permission_sets, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = DepartmentPermissionSetSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department permission sets retrieved successfully",
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
        serializer = DepartmentPermissionSetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Department permission set assigned successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department permission set assignment failed",
            errors=serializer.errors
        )


class DepartmentPermissionSetDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DepartmentPermissionSetSerializer

    def get_object(self, pk):
        return get_object_or_404(DepartmentPermissionSet, pk=pk)

    def get(self, request, pk):
        dept_permission_set = self.get_object(pk)
        serializer = DepartmentPermissionSetSerializer(dept_permission_set, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department permission set details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        dept_permission_set = self.get_object(pk)
        serializer = DepartmentPermissionSetSerializer(dept_permission_set, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Department permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department permission set update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        dept_permission_set = self.get_object(pk)
        serializer = DepartmentPermissionSetSerializer(dept_permission_set, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Department permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Department permission set update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        dept_permission_set = self.get_object(pk)
        dept_permission_set.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Department permission set deleted successfully"
        )
