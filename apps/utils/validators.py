import re

from django.conf import settings
from rest_framework import serializers


def password_validate(value):
    match = re.match(settings.PASSWORD_PATTERN, value)
    if not bool(match):
        raise serializers.ValidationError("Error: password")
