from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from company.models import Designation, DesignationPermissionSet
from company.serializers.designation import DesignationSerializer, DesignationPermissionSetSerializer
from company.views.company import standard_response


class DesignationListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DesignationSerializer
    page_size = 10

    def get(self, request):
        designations = Designation.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        department_param = request.query_params.get("department", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            designations = designations.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            designations = designations.filter(company=request.user.company)
        elif company_param:
            designations = designations.filter(company_id=company_param)

        if department_param:
            designations = designations.filter(department_id=department_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            designations = designations.filter(is_active=is_active)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(designations, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = DesignationSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designations retrieved successfully",
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
        serializer = DesignationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Designation created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation creation failed",
            errors=serializer.errors
        )


class DesignationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DesignationSerializer

    def get_object(self, pk):
        return get_object_or_404(Designation, pk=pk)

    def get(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designation details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Designation updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Designation updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        designation = self.get_object(pk)
        designation.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designation deleted successfully"
        )


class DesignationPermissionSetListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DesignationPermissionSetSerializer
    page_size = 10

    def get(self, request):
        desig_permission_sets = DesignationPermissionSet.objects.all()
        search_query = request.query_params.get("search", None)
        designation_param = request.query_params.get("designation", None)
        permission_set_param = request.query_params.get("permission_set", None)

        if search_query:
            desig_permission_sets = desig_permission_sets.filter(
                Q(designation__name__icontains=search_query) |
                Q(designation__code__icontains=search_query) |
                Q(permission_set__name__icontains=search_query) |
                Q(permission_set__code__icontains=search_query)
            )

        if designation_param:
            desig_permission_sets = desig_permission_sets.filter(designation_id=designation_param)

        if permission_set_param:
            desig_permission_sets = desig_permission_sets.filter(permission_set_id=permission_set_param)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(desig_permission_sets, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = DesignationPermissionSetSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designation permission sets retrieved successfully",
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
        serializer = DesignationPermissionSetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Designation permission set assigned successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation permission set assignment failed",
            errors=serializer.errors
        )


class DesignationPermissionSetDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DesignationPermissionSetSerializer

    def get_object(self, pk):
        return get_object_or_404(DesignationPermissionSet, pk=pk)

    def get(self, request, pk):
        desig_permission_set = self.get_object(pk)
        serializer = DesignationPermissionSetSerializer(desig_permission_set, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designation permission set details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        desig_permission_set = self.get_object(pk)
        serializer = DesignationPermissionSetSerializer(desig_permission_set, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Designation permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation permission set update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        desig_permission_set = self.get_object(pk)
        serializer = DesignationPermissionSetSerializer(desig_permission_set, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Designation permission set updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Designation permission set update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        desig_permission_set = self.get_object(pk)
        desig_permission_set.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Designation permission set deleted successfully"
        )
