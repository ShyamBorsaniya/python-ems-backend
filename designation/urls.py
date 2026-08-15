from django.urls import path
from .views import (
    DesignationListCreateView,
    DesignationDetailView,
    DesignationPermissionSetListCreateView,
    DesignationPermissionSetDetailView,
)

urlpatterns = [
    path('', DesignationListCreateView.as_view(), name='designation-list-create'),
    path('permission-sets/', DesignationPermissionSetListCreateView.as_view(), name='designation-permission-set-list-create'),
    path('permission-sets/<int:pk>/', DesignationPermissionSetDetailView.as_view(), name='designation-permission-set-detail'),
    path('<int:pk>/', DesignationDetailView.as_view(), name='designation-detail'),
]

