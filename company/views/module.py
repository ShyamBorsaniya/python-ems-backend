from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from company.models import Module
from company.serializers.module import ModuleSerializer
from company.views.company import standard_response


class ModuleListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ModuleSerializer
    page_size = 10

    def get(self, request):
        modules = Module.objects.select_related('company').all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        is_active_param = request.query_params.get("is_active", None)

        if search_query:
            modules = modules.filter(
                Q(name__icontains=search_query) |
                Q(display_name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            modules = modules.filter(Q(company=request.user.company) | Q(company__isnull=True))
        elif company_param:
            if company_param.lower() in ['null', 'none']:
                modules = modules.filter(company__isnull=True)
            else:
                modules = modules.filter(company_id=company_param)

        if is_active_param is not None:
            is_active = is_active_param.lower() in ["true", "1"]
            modules = modules.filter(is_active=is_active)

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(modules, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = ModuleSerializer(page.object_list, many=True, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Modules retrieved successfully",
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
        serializer = ModuleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Module created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Module creation failed",
            errors=serializer.errors
        )


class ModuleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ModuleSerializer

    def get_object(self, pk):
        return get_object_or_404(Module.objects.select_related('company'), pk=pk)

    def get(self, request, pk):
        module_obj = self.get_object(pk)
        serializer = ModuleSerializer(module_obj, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Module details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        module_obj = self.get_object(pk)
        serializer = ModuleSerializer(module_obj, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Module updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Module update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        module_obj = self.get_object(pk)
        serializer = ModuleSerializer(module_obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Module updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Module update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        module_obj = self.get_object(pk)
        module_obj.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Module deleted successfully"
        )
