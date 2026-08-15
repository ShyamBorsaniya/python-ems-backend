from django.urls import path
from .views import (
    PermissionSetListCreateView,
    PermissionSetDetailView,
    PermissionSetPermissionListCreateView,
    PermissionSetPermissionDetailView,
)

urlpatterns = [
    path('', PermissionSetListCreateView.as_view(), name='permission-set-list-create'),
    path('permissions/', PermissionSetPermissionListCreateView.as_view(), name='permission-set-permission-list-create'),
    path('permissions/<int:pk>/', PermissionSetPermissionDetailView.as_view(), name='permission-set-permission-detail'),
    path('<int:pk>/', PermissionSetDetailView.as_view(), name='permission-set-detail'),
]
