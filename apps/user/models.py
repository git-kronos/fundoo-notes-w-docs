from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models

from apps.utils.hash import JWT


# Create your models here.
class UserQuerySet(models.QuerySet):
    def all_notes(self, pk=None):
        if pk is None or pk == "":
            return self.none()
        obj = self.prefetch_related("collab", "notes").get(pk=pk)
        print(self.prefetch_related("collab", "notes").query)
        return obj.notes.all().union(obj.collab.all())


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(model=self.model, using=self._db)

    def all_notes(self, pk=None):
        return self.get_queryset().all_notes(pk=pk)

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    # username is optional
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_verified = models.BooleanField(default=False)
    objects = UserManager()

    @property
    def token(self):
        return JWT.encode(
            body={"id": self.pk, "email": self.email},
            aud=JWT.Aud.LOGIN,
        )
