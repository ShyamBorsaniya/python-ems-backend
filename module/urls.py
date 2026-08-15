from django.urls import path
from .views import ModuleListCreateView, ModuleDetailView

urlpatterns = [
    path('', ModuleListCreateView.as_view(), name='module-list-create'),
    path('<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
]
