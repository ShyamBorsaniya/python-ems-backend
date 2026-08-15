from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Employee
from .serializers import EmployeeSerializer


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


class EmployeeListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = EmployeeSerializer
    page_size = 10

    def get(self, request):
        employees = Employee.objects.all()

        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        department_param = request.query_params.get("department", None)
        designation_param = request.query_params.get("designation", None)
        emp_type_param = request.query_params.get("employment_type", None)
        emp_status_param = request.query_params.get("employment_status", None)
        gender_param = request.query_params.get("gender", None)

        if search_query:
            employees = employees.filter(
                Q(code__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(emergency_contact_name__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            employees = employees.filter(company=request.user.company)
        elif company_param:
            employees = employees.filter(company_id=company_param)

        if department_param:
            employees = employees.filter(department_id=department_param)

        if designation_param:
            employees = employees.filter(designation_id=designation_param)

        if emp_type_param:
            employees = employees.filter(employment_type=emp_type_param)

        if emp_status_param:
            employees = employees.filter(employment_status=emp_status_param)

        if gender_param:
            employees = employees.filter(gender=gender_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(employees, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = EmployeeSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Employees retrieved successfully",
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
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Employee profile created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee profile creation failed",
            errors=serializer.errors
        )


class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = EmployeeSerializer

    def get_object(self, pk):
        return get_object_or_404(Employee, pk=pk)

    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Employee details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Employee profile updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee profile update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Employee profile updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee profile update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Employee profile deleted successfully"
        )
