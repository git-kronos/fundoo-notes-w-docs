from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import decorators, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.user.serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    UserResponseSerializer,
    UserSerializer,
)
from apps.utils.auth import JwtAuthentication
from apps.utils.renderer import ApiRenderer

User = get_user_model()


# Create your views here.
@swagger_auto_schema(
    tags=["Auth"],
    method="POST",
    request_body=UserSerializer,
    responses={201: UserResponseSerializer()},
)
@decorators.api_view(["POST"])
@decorators.renderer_classes([ApiRenderer])
def user_register(request: Request) -> Response:
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    tags=["Auth"],
    method="POST",
    request_body=LoginSerializer,
    responses={202: LoginResponseSerializer()},
)
@decorators.api_view(["POST"])
def user_login(request: Request) -> Response:
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@swagger_auto_schema(
    tags=["User"],
    method="GET",
    responses={200: UserResponseSerializer()},
)
@decorators.api_view(["GET"])
@decorators.authentication_classes([JwtAuthentication])
@decorators.renderer_classes([ApiRenderer])
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
