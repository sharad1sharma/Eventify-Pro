from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from events.views import register_user

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("api/", TemplateView.as_view(template_name="index.html")),
    path("admin/", admin.site.urls),
    path("api/auth/register/", register_user, name="api-register"),
    path("api/auth/token/", obtain_auth_token, name="api-token-auth"),
    path("api/", include("events.urls")),
]
