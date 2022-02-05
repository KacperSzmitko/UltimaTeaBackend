"""ultima_tea URL Configuration

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
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView

from rest_framework import permissions
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os

class SchemaGenerator(OpenAPISchemaGenerator):
  def get_schema(self, request=None, public=False):
    schema = super(SchemaGenerator, self).get_schema(request, public)
    schema.basePath = os.path.join(schema.basePath, 'api/')
    return schema

schema_view = get_schema_view(
   openapi.Info(
      title="UltimaTea Server",
      default_version='v1',
      description="Server handeling all database manipulation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="ultimatea@gmail.com"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
#    urlconf="management_server.api.urls",
   generator_class=SchemaGenerator,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("admin/", admin.site.urls),
    path("", include("authorization.urls", namespace="auth")),
    path("", include("main_app.urls", namespace="main")),
]
