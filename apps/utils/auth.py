from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework.exceptions import APIException, AuthenticationFailed, NotFound

from apps.utils.hash import JWT


class JwtAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            model = get_user_model()
            auth_key = request.META.get("HTTP_AUTHORIZATION")
            if not auth_key:
                raise APIException("token is missing")
            scheme, token = auth_key.split()
            if scheme != "Bearer":
                raise APIException("invvalid scheme")

            payload = JWT.decode(token, aud=JWT.Aud.LOGIN)
            user = model.objects.filter(**payload["data"]).first()
            if not user:
                raise NotFound("No such user")
        except (model.DoesNotExist, APIException, NotFound) as e:
            raise AuthenticationFailed(detail=e.detail)
        return (user, token)
