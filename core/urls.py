"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/user/", include("user.urls")),
    path("api/users/", include("user.urls")),
    path("api/company/", include("company.urls")),
    path("api/department/", include("department.urls")),
    path("api/designation/", include("designation.urls")),
    path("api/role/", include("role.urls")),
    path("api/permission/", include("permission.urls")),
    path("api/project/", include("project.urls")),
    path("api/employees/", include("employee.urls")),
    path("api/modules/", include("module.urls")),
    path("api/permission-set/", include("permission_set.urls")),
    path("api/permission-sets/", include("permission_set.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

