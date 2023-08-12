from django.urls import path

from apps.note import views

app_name = "note"
urlpatterns = [
    path("", views.note_list, name="note-list"),
    path("<int:pk>", views.note_detail, name="note-detail"),
    path("<int:pk>/collab", views.collaborator_view, name="collab-note"),
    path("user", views.user_notes, name="user-note"),
]
