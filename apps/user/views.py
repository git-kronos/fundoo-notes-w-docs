from django.contrib.auth import get_user_model
from rest_framework import decorators, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.user.serializers import LoginSerializer, UserSerializer
from apps.utils.auth import JwtAuthentication

User = get_user_model()


# Create your views here.
@decorators.api_view(["POST"])
def user_register(request: Request) -> Response:
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST"])
def user_login(request: Request) -> Response:
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["GET"])
@decorators.authentication_classes([JwtAuthentication])
def user_profile(request: Request) -> Response:
    return Response(UserSerializer(request.user).data)


"""
@decorators.api_view(["POST"])
def set_password(request: Request):
    return Response({})


@decorators.api_view(["POST"])
def change_password(request: Request):
    return Response({})
 """
