from django.urls import path

from apps.note import views

app_name = "note"
urlpatterns = [
    path("", views.note_list, name="note-list"),
    path("<int:pk>", views.note_detail, name="note-detail"),
    path("user", views.user_notes, name="user-note"),
]
