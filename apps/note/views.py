from functools import wraps

from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
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
    def wrapper(request: Request, *a, **kw):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
            request.data.appendlist("owner", request.user.id)
            request.data._mutable = False
        elif isinstance(request.data, dict):
            request.data["owner"] = request.user.id
        return f(request, *a, **kw)

    return wrapper


"""
class NoteListView(generics.GenericAPIView):
    authentication_classes = [JwtAuthentication]
    renderer_classes = [ApiRenderer]
    pagination_class = StandardPagination
    serializer_class = NoteSerializer

    def get_queryset(self):
        return get_notes_by_user(self.request.user)

    @property
    def serialized_response(self):
        return SerializedResponse(self.serializer_class)

    def get(self, request):
        qs = self.paginate_queryset(self.get_queryset())
        serializer = NoteSerializer(qs, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(update_user_input)
    def post(self, request, *args, **kwargs):
        return self.serialized_response.post(request.data)


class NoteDetailView(generics.GenericAPIView):
    authentication_classes = [JwtAuthentication]
    renderer_classes = [ApiRenderer]
    serializer_class = NoteSerializer
    lookup_field = "pk"

    @property
    def serialized_response(self):
        return SerializedResponse(self.serializer_class, self.get_object())

    def get_queryset(self):
        return get_notes_by_user(self.request.user)

    def get(self, request, pk=None):
        return self.serialized_response.get()

    @method_decorator(update_user_input)
    def put(self, request, pk=None):
        return self.serialized_response.put(request.data)

    @method_decorator(update_user_input)
    def delete(self, request, pk=None):
        return self.serialized_response.delete()


class UserNoteView(generics.GenericAPIView):
    authentication_classes = [JwtAuthentication]
    renderer_classes = [ApiRenderer]
    serializer_class = ProfileSerializer

    def get(self, request):
        serializer = ProfileSerializer(instance=request.user)
        return response.Response(serializer.data)


class CollaboratorView(generics.GenericAPIView):
    authentication_classes = (JwtAuthentication,)
    renderer_classes = (ApiRenderer,)
    serializer_class = CollaboratorSerializer
    lookup_field = "pk"

    def get_object(self):
        lookup = self.lookup_field
        filter = {lookup: self.kwargs[lookup]}
        obj = get_object_or_404(Note, **filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def _collaborator_action(self, action, payload):
        serializer = self.serializer_class(
            instance=self.get_object(),
            data=payload,
            context={"action": action},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=202)

    def post(self, request, pk):
        return self._collaborator_action(action="add", payload=request.data)

    def delete(self, request, pk):
        return self._collaborator_action(action="remove", payload=request.data)

"""


class NoteModelViewSet(ModelViewSet):
    authentication_classes = (JwtAuthentication,)
    renderer_classes = (ApiRenderer,)
    pagination_class = StandardPagination
    lookup_field = "pk"  # pk is the default value and can be changed.
    serializer_class = NoteSerializer
    collab_serializer_class = CollaboratorSerializer  # custom attr

    # queryset = Note.objects.all() # queryset/get_queryset() is mandatory
    def get_queryset(self):
        return Note.objects.owner_notes(owner=self.request.user)

    # no need to define `list`,`retrieve`,`update` we are depending on default logic

    @method_decorator(update_user_input, name="create")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(update_user_input, name="update")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(method="GET", responses={200: ProfileSerializer()})
    @action(methods=["GET"], detail=False, url_name="user")
    def user_notes(self, request):
        sr = SerializedResponse(ProfileSerializer, request.user)
        return sr.get()

    @swagger_auto_schema(methods=["POST", "DELETE"], responses={202: CollaboratorSerializer()})
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="collab",
        url_name="collab",
    )
    def update_collab(self, request, pk=None):
        actions = {"POST": "add", "DELETE": "remove"}
        action = actions.get(request.method)
        obj = get_object_or_404(Note, pk=pk)
        sr = SerializedResponse(self.collab_serializer_class, obj)
        response = sr.put(request.data, context={"action": action})
        collaborator_signals.send(sender=self.__class__, payload={"data": response.data, "action": action})
        return response
