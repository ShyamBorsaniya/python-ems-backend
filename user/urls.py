from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, UserListView, UserDetailView, UserRestoreView,
    PendingUserListView, UserApproveView, UserRejectView
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("pending/", PendingUserListView.as_view(), name="user-pending-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/restore/", UserRestoreView.as_view(), name="user-restore"),
    path("<int:pk>/approve/", UserApproveView.as_view(), name="user-approve"),
    path("<int:pk>/reject/", UserRejectView.as_view(), name="user-reject"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]