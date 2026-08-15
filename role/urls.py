from django.urls import path
from .views import (
    RoleListCreateView,
    RoleDetailView,
    RolePermissionListCreateView,
    RolePermissionDetailView,
    RolePermissionSetListCreateView,
    RolePermissionSetDetailView,
)

urlpatterns = [
    path('', RoleListCreateView.as_view(), name='role-list-create'),
    path('permissions/', RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('permissions/<int:pk>/', RolePermissionDetailView.as_view(), name='role-permission-detail'),
    path('permission-sets/', RolePermissionSetListCreateView.as_view(), name='role-permission-set-list-create'),
    path('permission-sets/<int:pk>/', RolePermissionSetDetailView.as_view(), name='role-permission-set-detail'),
    path('<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]


