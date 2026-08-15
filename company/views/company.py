from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from company.models import Company
from company.serializers import CompanySerializer


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


class CompanyListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        companies = Company.objects.all()
        search_query = request.query_params.get("search", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            companies = companies.filter(
                name__icontains=search_query
            ) | companies.filter(
                code__icontains=search_query
            )

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            companies = companies.filter(is_active=is_active)

        serializer = CompanySerializer(companies, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Companies retrieved successfully",
            data=serializer.data
        )

    def post(self, request):
        serializer = CompanySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            company = serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Company created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Company creation failed",
            errors=serializer.errors
        )


class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CompanySerializer

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Company details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Company updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Company update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Company updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Company update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        company = self.get_object(pk)
        company.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Company deleted successfully"
        )
