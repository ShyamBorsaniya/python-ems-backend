from django.urls import path
from .views import (
    RoleListCreateView,
    RoleDetailView,
    RolePermissionSetListCreateView,
    RolePermissionSetDetailView,
)

urlpatterns = [
    path('', RoleListCreateView.as_view(), name='role-list-create'),
    path('permission-sets/', RolePermissionSetListCreateView.as_view(), name='role-permission-set-list-create'),
    path('permission-sets/<int:pk>/', RolePermissionSetDetailView.as_view(), name='role-permission-set-detail'),
    path('<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]


