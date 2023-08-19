# from django.urls import path

from rest_framework import routers

from apps.note.views import NoteModelViewSet

app_name = "note"

# list_views = {"get": "list", "post": "create"}
# detail_views = {"get": "retrieve", "put": "update", "delete": "destroy"}
# update_collab = {"post": "update_collab", "delete": "update_collab"}
# urlpatterns = [
#     path(
#         "",
#         NoteModelViewSet.as_view(list_views),
#         name="note-list",
#     ),
#     path(
#         "user",
#         NoteModelViewSet.as_view({"get": "user_notes"}),
#         name="user-note",
#     ),
#     path(
#         "<int:pk>",
#         NoteModelViewSet.as_view(detail_views),
#         name="note-detail",
#     ),
#     path(
#         "<int:pk>/collab",
#         NoteModelViewSet.as_view(update_collab),
#         name="collab-note",
#     ),
# ]

router = routers.SimpleRouter()
router.register(prefix="", viewset=NoteModelViewSet, basename="note")
urlpatterns = router.urls
