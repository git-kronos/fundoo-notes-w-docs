from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(public=True, permission_classes=(AllowAny,))

urlpatterns = [
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("api/note/", include("apps.note.urls", namespace="note")),
    path("api/", include("apps.user.urls", namespace="user")),
]
