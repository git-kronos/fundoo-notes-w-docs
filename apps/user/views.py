from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.user.serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    UserResponseSerializer,
    UserSerializer,
)
from apps.utils import ApiRenderer, JwtAuthentication, SerializedResponse, JWT

User = get_user_model()


# Create your views here.
class RegisterAPIView(APIView):
    renderer_classes = [ApiRenderer]
    serialized_response = SerializedResponse(UserSerializer)

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=UserSerializer,
        responses={201: UserResponseSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return self.serialized_response.post(request.data)


class LoginAPIView(APIView):
    serialized_response = SerializedResponse(LoginSerializer)

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=LoginSerializer,
        responses={202: LoginResponseSerializer()},
    )
    def post(self, request):
        return self.serialized_response.post(payload=request.data, status=202)


class ProfileAPIView(APIView):
    authentication_classes = [JwtAuthentication]
    renderer_classes = [ApiRenderer]

    @swagger_auto_schema(
        tags=["User"], responses={200: UserResponseSerializer()}
    )
    def get(self, request):
        serialized_response = SerializedResponse(
            UserSerializer,
            request.user,
        )
        return serialized_response.get()


def verify_user(request, token):
    payload = JWT.decode(token, aud=JWT.Aud.VERIFY)
    user = get_object_or_404(User, **payload['data'])
    user.is_verified = True
    user.save()
    return HttpResponse('Verification successfully')
