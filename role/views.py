from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Role
from .serializers import RoleSerializer


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

    def get(self, request):
        roles = Role.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)

        if search_query:
            roles = roles.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        if company_param:
            roles = roles.filter(company_id=company_param)

        serializer = RoleSerializer(roles, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Roles retrieved successfully",
            data=serializer.data
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
        role.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Role deleted successfully"
        )
