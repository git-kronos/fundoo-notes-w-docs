from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from apps.utils.validators import password_validate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        )
        read_only_fields = ("id", "is_staff", "is_active")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "validators": [password_validate],
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        validators=[password_validate],
    )

    def create(self, credentials: dict):
        user = authenticate(**credentials)
        if not user:
            raise AuthenticationFailed()
        return user
