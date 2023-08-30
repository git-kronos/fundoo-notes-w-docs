from functools import partial, wraps

from django.conf import settings
from django.core.cache import cache
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from apps.note.models import Note
from apps.note.serializers import (
    CollaboratorSerializer,
    NoteSerializer,
    ProfileSerializer,
)
from apps.utils import (
    ApiRenderer,
    JwtAuthentication,
    SerializedResponse,
    StandardPagination,
    collaborator_signals,
)


# Create your views here.
def update_user_input(f):
    @wraps(f)
    def wrapper(request, *a, **kw):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
            request.data.appendlist("owner", request.user.id)
            request.data._mutable = False
        elif isinstance(request.data, dict):
            request.data["owner"] = request.user.id
        return f(request, *a, **kw)

    return wrapper


# LINK - https://github.com/jazzband/django-redis#scan--delete-keys-in-bulk
def delete_cache(f):
    """
    Delete all cache keys with the given prefix.
    """

    key_prefix = "note-view"
    pattern_str = "views.decorators.cache.cache_*.%(prefix)s.*.%(lang)s.%(tz)s"

    def wrapper(request, *args, **kwargs):
        response = f(request, *args, **kwargs)
        if 200 <= response.status_code < 300:
            pattern = pattern_str % {"prefix": key_prefix, "lang": settings.LANGUAGE_CODE, "tz": settings.TIME_ZONE}
            cache.delete(pattern)
        return response

    return wrapper


cache_partial = partial(cache_page, key_prefix="note-view")


@method_decorator(cache_partial(settings.CACHE_TTL), name="list")
@method_decorator(cache_partial(settings.CACHE_TTL), name="retrieve")
@method_decorator([update_user_input, delete_cache], name="create")
@method_decorator([update_user_input, delete_cache], name="update")
@method_decorator([update_user_input, delete_cache], name="destroy")
class NoteModelViewSet(ModelViewSet):
    authentication_classes = (JwtAuthentication,)
    renderer_classes = (ApiRenderer,)
    pagination_class = StandardPagination
    lookup_field = "pk"
    serializer_class = NoteSerializer
    collab_serializer_class = CollaboratorSerializer

    def get_queryset(self):
        return Note.objects.owner_notes(owner=self.request.user)

    @swagger_auto_schema(method="GET", responses={200: ProfileSerializer()})
    @action(methods=["GET"], detail=False, url_name="user")
    def user_notes(self, request):
        sr = SerializedResponse(ProfileSerializer, request.user)
        return sr.get()

    @swagger_auto_schema(methods=["POST", "DELETE"], responses={202: CollaboratorSerializer()})
    @action(detail=True, methods=["POST", "DELETE"], url_path="collab", url_name="collab")
    def update_collab(self, request, pk=None):
        actions = {"POST": "add", "DELETE": "remove"}
        action = actions.get(request.method)
        obj = get_object_or_404(Note, pk=pk)
        sr = SerializedResponse(self.collab_serializer_class, obj)
        response = sr.put(request.data, context={"action": action})
        collaborator_signals.send(sender=self.__class__, payload={"data": response.data, "action": action})
        return response
