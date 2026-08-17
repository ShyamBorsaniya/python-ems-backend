from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from company.models import Project, ProjectMember
from company.serializers.project import ProjectSerializer, ProjectMemberSerializer
from company.views.company import standard_response
from company.mixins import PermissionCheckMixin


class ProjectListCreateView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProjectSerializer
    page_size = 10
    module_code = 'project_management'

    def get(self, request):
        perm_error = self.check_permission(request, action='view')
        if perm_error:
            return perm_error

        projects = Project.objects.all()
        search_query = request.query_params.get("search", None)
        company_param = request.query_params.get("company", None)
        status_param = request.query_params.get("status", None)
        priority_param = request.query_params.get("priority", None)

        if search_query:
            projects = projects.filter(
                Q(name__icontains=search_query) | Q(code__icontains=search_query) | Q(description__icontains=search_query)
            )

        if getattr(request.user, 'company', None):
            projects = projects.filter(company=request.user.company)
        elif company_param:
            projects = projects.filter(company_id=company_param)

        if status_param:
            projects = projects.filter(status=status_param.upper())

        if priority_param:
            projects = projects.filter(priority=priority_param.upper())

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(projects, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = ProjectSerializer(page.object_list, many=True, context={'request': request})

        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Projects retrieved successfully",
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

        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Project created successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project creation failed",
            errors=serializer.errors
        )


class ProjectDetailView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProjectSerializer
    module_code = 'project_management'

    def get_object(self, pk):
        return get_object_or_404(Project, pk=pk)

    def get(self, request, pk):
        perm_error = self.check_permission(request, action='view')
        if perm_error:
            return perm_error

        project = self.get_object(pk)
        serializer = ProjectSerializer(project, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Project details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        perm_error = self.check_permission(request, action='edit')
        if perm_error:
            return perm_error

        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Project updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        perm_error = self.check_permission(request, action='edit')
        if perm_error:
            return perm_error

        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Project updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        perm_error = self.check_permission(request, action='delete')
        if perm_error:
            return perm_error

        project = self.get_object(pk)
        project.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Project deleted successfully"
        )


class ProjectMemberListCreateView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProjectMemberSerializer
    page_size = 10
    module_code = 'project_management'

    def get(self, request):
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        members = ProjectMember.objects.select_related('project', 'employee').all()
        project_param = request.query_params.get("project", None)
        employee_param = request.query_params.get("employee", None)
        role_param = request.query_params.get("role", None)
        search_query = request.query_params.get("search", None)

        if project_param:
            members = members.filter(project_id=project_param)

        if employee_param:
            members = members.filter(employee_id=employee_param)

        if role_param:
            members = members.filter(role_in_project__icontains=role_param)

        if search_query:
            members = members.filter(
                Q(project__name__icontains=search_query) |
                Q(project__code__icontains=search_query) |
                Q(employee__user__first_name__icontains=search_query) |
                Q(employee__user__last_name__icontains=search_query) |
                Q(role_in_project__icontains=search_query)
            )

        page_size_param = request.query_params.get("page_size", None)
        if page_size_param:
            try:
                page_size = int(page_size_param)
            except (ValueError, TypeError):
                page_size = self.page_size
        else:
            page_size = self.page_size

        paginator = Paginator(members, page_size)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        serializer = ProjectMemberSerializer(page.object_list, many=True, context={'request': request})

        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Project members retrieved successfully",
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
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        serializer = ProjectMemberSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_201_CREATED,
                message="Project member added successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project member addition failed",
            errors=serializer.errors
        )


class ProjectMemberDetailView(PermissionCheckMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProjectMemberSerializer
    module_code = 'project_management'

    def get_object(self, pk):
        return get_object_or_404(ProjectMember, pk=pk)

    def get(self, request, pk):
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        member = self.get_object(pk)
        serializer = ProjectMemberSerializer(member, context={'request': request})
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Project member details retrieved successfully",
            data=serializer.data
        )

    def put(self, request, pk):
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        member = self.get_object(pk)
        serializer = ProjectMemberSerializer(member, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Project member updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project member update failed",
            errors=serializer.errors
        )

    def patch(self, request, pk):
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        member = self.get_object(pk)
        serializer = ProjectMemberSerializer(member, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                status_code=status.HTTP_200_OK,
                message="Project member updated successfully",
                data=serializer.data
            )
        return standard_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Project member update failed",
            errors=serializer.errors
        )

    def delete(self, request, pk):
        perm_error = self.check_permission(request, action='manage_members')
        if perm_error:
            return perm_error

        member = self.get_object(pk)
        member.delete()
        return standard_response(
            status_code=status.HTTP_200_OK,
            message="Project member removed successfully"
        )
