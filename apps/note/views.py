from typing import Union

from django.shortcuts import get_object_or_404
from rest_framework import decorators, exceptions
from rest_framework.request import Request
from rest_framework.response import Response

from apps.note import serializers
from apps.note.models import Note, Profile
from apps.note.serializers import NoteSerializer, ProfileSerializer


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


@decorators.api_view(["GET", "POST"])
def note_list(request: Request):
    payload = {"status": 200, "data": None}

    if request.method == "GET":
        payload["data"] = NoteCRUD.list()
    if request.method == "POST":
        print("?????", request.data)
        payload.update(
            data=NoteCRUD.create(request.data),
            status=201,
        )
    return Response(**payload)


@decorators.api_view(["GET"])
def user_notes(request: Request, pk: int):
    obj = get_object_or_404(Profile, pk=pk)
    serializer = ProfileSerializer(instance=obj)
    return Response(serializer.data)


"""
Apis with pk/id values
"""


@decorators.api_view(["GET", "PUT", "DELETE"])
def note_detail(request: Request, pk: Union[int, str]):
    payload = {"status": 200, "data": None}

    # retrieve data
    if request.method == "GET":
        payload["data"] = NoteCRUD.retrieve(pk)

    # update data
    if request.method == "PUT":
        payload.update(
            data=NoteCRUD.update(pk, data=request.data),
            status=202,
        )

    # delete data
    if request.method == "DELETE":
        payload.update(data=NoteCRUD.delete(pk), status=204)

    return Response(**payload)
