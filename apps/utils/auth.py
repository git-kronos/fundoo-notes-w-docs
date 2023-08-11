from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import APIException, AuthenticationFailed

from apps.utils.hash import JWT


class JwtAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        model = get_user_model()

        auth_key: str = request.META.get("HTTP_AUTHORIZATION")
        scheme, token = auth_key.split()
        if scheme != "Bearer":
            raise APIException("invvalid scheme")

        payload = JWT.decode(token, aud=JWT.Aud.LOGIN)
        try:
            user = model.objects.get(**payload["data"])
        except model.DoesNotExist:
            raise AuthenticationFailed("No such user")
        return (user, token)
