from rest_framework.exceptions import APIException
from rest_framework.response import Response


class SerializedResponse:
    def __init__(self, serializer_klass=None, instance=None):
        self._serializer_klass = serializer_klass
        self._instance = instance

    @property
    def serializer_klass(self):
        if not self._serializer_klass:
            raise APIException("serializer_klass is missing", "invalid_arg")
        return self._serializer_klass

    @property
    def instance(self):
        if not self._instance:
            raise APIException("instance is missing", "invalid_arg")
        return self._instance

    def post(self, payload, status=201, context=None):
        serializer = self.serializer_klass(data=payload, context=context or {})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status)

    def get(self, qs=None, status=200, many=False):
        if many is True and qs is None:
            raise APIException("qs param required!!", "invalid_arg")

        obj = qs or self.instance
        serializer = self.serializer_klass(obj, many=many)
        return Response(serializer.data, status=status)

    def put(self, payload, status=202, context=None):
        serializer = self.serializer_klass(
            self.instance, data=payload, context=context or None
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status)

    def delete(self):
        self.instance.delete()
        return Response(status=204)
