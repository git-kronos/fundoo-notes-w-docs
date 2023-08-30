# from django.urls import path

from rest_framework import routers

from apps.note.views import NoteModelViewSet

app_name = "note"


router = routers.SimpleRouter(trailing_slash=False)
router.register(prefix="", viewset=NoteModelViewSet, basename="note")
urlpatterns = router.urls
