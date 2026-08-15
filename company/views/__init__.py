from .company import CompanyListCreateView, CompanyDetailView, standard_response
from .user import (
    RegisterView, LoginView, UserListView, UserDetailView, UserRestoreView,
    PendingUserListView, UserApproveView, UserRejectView
)
from .department import (
    DepartmentListCreateView, DepartmentDetailView,
    DepartmentPermissionSetListCreateView, DepartmentPermissionSetDetailView
)
from .designation import (
    DesignationListCreateView, DesignationDetailView,
    DesignationPermissionSetListCreateView, DesignationPermissionSetDetailView
)
from .role import (
    RoleListCreateView, RoleDetailView,
    RolePermissionSetListCreateView, RolePermissionSetDetailView
)
from .permission import PermissionListCreateView, PermissionDetailView
from .permission_set import (
    PermissionSetListCreateView, PermissionSetDetailView,
    PermissionSetPermissionListCreateView, PermissionSetPermissionDetailView
)
from .project import (
    ProjectListCreateView, ProjectDetailView,
    ProjectMemberListCreateView, ProjectMemberDetailView
)
from .employee import EmployeeListCreateView, EmployeeDetailView
from .module import ModuleListCreateView, ModuleDetailView
