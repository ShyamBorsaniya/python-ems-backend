from django.urls import path
from .views import (
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentPermissionSetListCreateView,
    DepartmentPermissionSetDetailView,
)

urlpatterns = [
    path('', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('permission-sets/', DepartmentPermissionSetListCreateView.as_view(), name='department-permission-set-list-create'),
    path('permission-sets/<int:pk>/', DepartmentPermissionSetDetailView.as_view(), name='department-permission-set-detail'),
    path('<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
]

