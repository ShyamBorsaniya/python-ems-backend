from django.urls import path
from .views import PermissionListCreateView, PermissionDetailView

urlpatterns = [
    path('', PermissionListCreateView.as_view(), name='permission-list-create'),
    path('<int:pk>/', PermissionDetailView.as_view(), name='permission-detail'),
]
