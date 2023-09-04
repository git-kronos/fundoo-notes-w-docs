from django.urls import path

from apps.note import views

app_name = "note"


urlpatterns = [
    path("", views.list_note),
    path("<int:pk>", views.detail_note),
]
