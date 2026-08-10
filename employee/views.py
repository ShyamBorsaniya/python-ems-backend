from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

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

    def get(self, request):
        employees = Employee.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        department_param = request.query_params.get("department", None)
        status_param = request.query_params.get("status", None)
        employment_type_param = request.query_params.get("employment_type", None)
        gender_param = request.query_params.get("gender", None)

        if search_query:
            employees = employees.filter(
                Q(employee_code__icontains=search_query) |
                Q(designation__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(emergency_contact_name__icontains=search_query)
            )

        if company_param:
            employees = employees.filter(company_id=company_param)

        if department_param:
            employees = employees.filter(department_id=department_param)

        if status_param:
            employees = employees.filter(status=status_param.upper())

        if employment_type_param:
            employees = employees.filter(employment_type=employment_type_param.upper())

        if gender_param:
            employees = employees.filter(gender__iexact=gender_param)

        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Employees retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Employee created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee creation failed",
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
                message="Employee updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Employee updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Employee update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Employee deleted successfully"
        )
