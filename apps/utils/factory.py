import factory

from apps.note.models import Note
from apps.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda a: "{}.{}@example.com".format(a.first_name, a.last_name).lower())
    password = factory.PostGenerationMethodCall("set_password", "Password@12")
    is_superuser = False
    is_staff = False
    is_active = True


class AdminFactory(UserFactory):
    is_superuser = True
    is_staff = True


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Faker("sentence", nb_words=4)
    body = factory.Faker("sentence", nb_words=10)
    owner = factory.SubFactory(UserFactory)
