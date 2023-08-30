from datetime import datetime
from enum import Enum

import jwt
from django.conf import settings
from rest_framework.exceptions import APIException

KEY = settings.JWT_CONFIG["key"]
ALGORITHMS = settings.JWT_CONFIG["algorithms"]
EXP = settings.JWT_CONFIG["exp"]


class JWT:
    class Aud(str, Enum):
        REGISTER = "USER:register"
        LOGIN = "login"
        VERIFY = "user_verification"

    @staticmethod
    def encode(body: dict, aud: Aud, exp: datetime = None) -> str:  # type: ignore
        payload = {"exp": exp or datetime.now() + EXP, "aud": aud, "data": body}
        return jwt.encode(payload, key=KEY)

    @staticmethod
    def decode(encoded_string: str, aud: Aud):
        try:
            payload = jwt.decode(encoded_string, key=KEY, algorithms=ALGORITHMS, audience=aud)
        except jwt.PyJWTError as e:
            raise APIException(detail=e.args[0])
        return payload
