# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

"""package_info_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter
from api import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="PKGman API",
        default_version='v1',
        description="Useful info for Linux distributions packages",
        contact=openapi.Contact(email="itp20126@hua.gr"),
        license=openapi.License(name="Copyright 2021 - Ioannis Papadopoulos - AGPL-3.0-or-later"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


package_router = SimpleRouter()
package_router.register(r'packages/versions/ratings', views.RatingViewSet)
package_router.register(r'packages/versions', views.PackageVersionViewSet)
package_router.register(r'packages', views.PackageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/users/', include('users.urls', namespace='users')),
    re_path(r'^api/v1/', include(package_router.urls)),
    re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
