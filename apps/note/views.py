from functools import wraps

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import decorators
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.request import Request
from rest_framework.response import Response

from apps.note.models import Note
from apps.note.serializers import (
    NoteResponseSerializer,
    NoteSerializer,
    ProfileSerializer,
)
from apps.utils.auth import JwtAuthentication


# Create your views here.
class NoteCRUD:
    @staticmethod
    def create(data: dict):
        """
        content of data:
            title: str,
            body: str,
            owner: int
        """
        # try:
        #     data["owner_id"] = data.pop("owner")
        # except KeyError as e:
        #     raise exceptions.APIException(
        #         detail=f"Error field: `{e.args[0]}`",
        #         code="invalid_key",
        #     )

        # obj = Note.objects.create(**data)
        """
        Alternative:
        obj = Note(**data)
        obj.save()
        """
        serializer = NoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @staticmethod
    def list():
        """
        `get_list_or_404()` -> list[object] or raise Http404 error
        > alternative:
        ```python
            qs = Note.objects.all()
            if not qs.exists():
                raise exceptions.NotFound()
        ```

        Notable method can be use against `all()`:
        `values()`, `values_list()`, `select_related()`

        Note: use `select_related()` for query having relationship
        """

        qs = Note.objects.all()
        serializer = NoteSerializer(qs, many=True)
        return serializer.data

    @staticmethod
    def retrieve(pk: int):
        """
        `get_object_or_404()` -> object or raise Http404 error
        > alternative:
        ```python
        try:
            return Note.objects.get(pk=pk)
        except Note.DoesNotExist:
            raise exceptions.NotFound()
        ```
        """

        obj = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(obj)
        return serializer.data

    @staticmethod
    def update(pk: int, data: dict):
        obj = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @staticmethod
    def delete(pk: int):
        obj = get_object_or_404(Note, pk=pk)
        obj.delete()
        return None


"""
Apis without pk/id values
"""


def update_user_input(f):
    @wraps(f)
    def wrapper(request: Request, *a, **kw):
        request.data["owner"] = request.user.id
        return f(request, *a, **kw)

    return wrapper


@swagger_auto_schema(
    method="GET", responses={200: NoteResponseSerializer(many=True)}
)
@swagger_auto_schema(
    method="POST",
    request_body=NoteSerializer,
    responses={201: NoteResponseSerializer},
)
@decorators.api_view(["GET", "POST"])
@decorators.authentication_classes([JwtAuthentication])
@update_user_input
def note_list(request: Request) -> Response:
    payload = {"status": 200, "data": None}
    match request.method:
        case "GET":
            payload["data"] = NoteCRUD.list()
        case "POST":
            payload.update(data=NoteCRUD.create(request.data), status=201)
        case _:
            raise MethodNotAllowed()
    return Response(**payload)


@swagger_auto_schema(method="GET", responses={200: ProfileSerializer})
@decorators.api_view(["GET"])
@decorators.authentication_classes([JwtAuthentication])
def user_notes(request: Request) -> Response:
    serializer = ProfileSerializer(instance=request.user)
    return Response(serializer.data)


"""
Apis with pk/id values
"""


@swagger_auto_schema(method="GET", responses={200: NoteResponseSerializer})
@swagger_auto_schema(
    method="PUT",
    request_body=NoteSerializer,
    responses={202: NoteResponseSerializer},
)
@decorators.api_view(["GET", "PUT", "DELETE"])
@decorators.authentication_classes([JwtAuthentication])
@update_user_input
def note_detail(request: Request, pk: int) -> Response:
    payload = {"status": 200, "data": None}

    match request.method:
        case "GET":
            # retrieve data
            payload["data"] = NoteCRUD.retrieve(pk)
        case "PUT":
            # update data
            payload.update(
                data=NoteCRUD.update(pk, data=request.data), status=202
            )
        case "DELETE":
            # delete data
            payload.update(data=NoteCRUD.delete(pk), status=204)
        case _:
            raise MethodNotAllowed()

    return Response(**payload)
