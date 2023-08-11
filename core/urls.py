from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/note/", include("apps.note.urls", namespace="note")),
    path("api/", include("apps.user.urls", namespace="user")),
]
