from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from company.views import (
    CompanyListCreateView, CompanyDetailView, PublicCompanyListView,
    RegisterView, LoginView, UserListView, UserDetailView, UserRestoreView,
    PendingUserListView, UserApproveView, UserRejectView,
    DepartmentListCreateView, DepartmentDetailView,
    DepartmentPermissionSetListCreateView, DepartmentPermissionSetDetailView,
    DesignationListCreateView, DesignationDetailView,
    DesignationPermissionSetListCreateView, DesignationPermissionSetDetailView,
    RoleListCreateView, RoleDetailView,
    RolePermissionSetListCreateView, RolePermissionSetDetailView,
    PermissionListCreateView, PermissionDetailView,
    PermissionSetListCreateView, PermissionSetDetailView,
    PermissionSetPermissionListCreateView, PermissionSetPermissionDetailView,
    ProjectListCreateView, ProjectDetailView,
    ProjectMemberListCreateView, ProjectMemberDetailView,
    EmployeeListCreateView, EmployeeDetailView,
    ModuleListCreateView, ModuleDetailView
)

urlpatterns = [
    # Company URLs
    path('company/', CompanyListCreateView.as_view(), name='company-list-create'),
    path('company/public/', PublicCompanyListView.as_view(), name='public-company-list'),
    path('public/companies/', PublicCompanyListView.as_view(), name='public-companies-list'),
    path('company/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),

    # User URLs
    path('user/', UserListView.as_view(), name='user-list'),
    path('users/', UserListView.as_view(), name='users-list'),
    path('user/pending/', PendingUserListView.as_view(), name='user-pending-list'),
    path('users/pending/', PendingUserListView.as_view(), name='users-pending-list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='users-detail'),
    path('user/<int:pk>/restore/', UserRestoreView.as_view(), name='user-restore'),
    path('users/<int:pk>/restore/', UserRestoreView.as_view(), name='users-restore'),
    path('user/<int:pk>/approve/', UserApproveView.as_view(), name='user-approve'),
    path('users/<int:pk>/approve/', UserApproveView.as_view(), name='users-approve'),
    path('user/<int:pk>/reject/', UserRejectView.as_view(), name='user-reject'),
    path('users/<int:pk>/reject/', UserRejectView.as_view(), name='users-reject'),
    path('user/register/', RegisterView.as_view(), name='register'),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Department URLs
    path('department/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('department/permission-sets/', DepartmentPermissionSetListCreateView.as_view(), name='department-permission-set-list-create'),
    path('department/permission-sets/<int:pk>/', DepartmentPermissionSetDetailView.as_view(), name='department-permission-set-detail'),
    path('department/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),

    # Designation URLs
    path('designation/', DesignationListCreateView.as_view(), name='designation-list-create'),
    path('designation/permission-sets/', DesignationPermissionSetListCreateView.as_view(), name='designation-permission-set-list-create'),
    path('designation/permission-sets/<int:pk>/', DesignationPermissionSetDetailView.as_view(), name='designation-permission-set-detail'),
    path('designation/<int:pk>/', DesignationDetailView.as_view(), name='designation-detail'),

    # Role URLs
    path('role/', RoleListCreateView.as_view(), name='role-list-create'),
    path('role/permission-sets/', RolePermissionSetListCreateView.as_view(), name='role-permission-set-list-create'),
    path('role/permission-sets/<int:pk>/', RolePermissionSetDetailView.as_view(), name='role-permission-set-detail'),
    path('role/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),

    # Permission URLs
    path('permission/', PermissionListCreateView.as_view(), name='permission-list-create'),
    path('permission/<int:pk>/', PermissionDetailView.as_view(), name='permission-detail'),

    # Project URLs
    path('project/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('project/members/', ProjectMemberListCreateView.as_view(), name='project-member-list-create'),
    path('project/members/<int:pk>/', ProjectMemberDetailView.as_view(), name='project-member-detail'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    # Employees URLs
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),

    # Modules URLs
    path('modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),

    # Permission Set URLs
    path('permission-set/', PermissionSetListCreateView.as_view(), name='permission-set-list-create'),
    path('permission-set/permissions/', PermissionSetPermissionListCreateView.as_view(), name='permission-set-permission-list-create'),
    path('permission-set/permissions/<int:pk>/', PermissionSetPermissionDetailView.as_view(), name='permission-set-permission-detail'),
    path('permission-set/<int:pk>/', PermissionSetDetailView.as_view(), name='permission-set-detail'),

    path('permission-sets/', PermissionSetListCreateView.as_view(), name='permission-sets-list-create'),
    path('permission-sets/permissions/', PermissionSetPermissionListCreateView.as_view(), name='permission-sets-permission-list-create'),
    path('permission-sets/permissions/<int:pk>/', PermissionSetPermissionDetailView.as_view(), name='permission-sets-permission-detail'),
    path('permission-sets/<int:pk>/', PermissionSetDetailView.as_view(), name='permission-sets-detail'),
]
