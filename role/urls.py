from django.urls import path
from .views import (
    RoleListCreateView,
    RoleDetailView,
    RolePermissionListCreateView,
    RolePermissionDetailView,
)

urlpatterns = [
    path('', RoleListCreateView.as_view(), name='role-list-create'),
    path('permissions/', RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('permissions/<int:pk>/', RolePermissionDetailView.as_view(), name='role-permission-detail'),
    path('<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]

