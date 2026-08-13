from django.urls import path
from .views import DesignationListCreateView, DesignationDetailView

urlpatterns = [
    path('', DesignationListCreateView.as_view(), name='designation-list-create'),
    path('<int:pk>/', DesignationDetailView.as_view(), name='designation-detail'),
]
