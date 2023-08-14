import pytest
from django.contrib.auth import get_user_model
from faker import Faker

from apps.utils.factory import NoteFactory, UserFactory

fake = Faker()
User = get_user_model()


@pytest.fixture
def user():
    yield UserFactory.create()


@pytest.fixture
def note(user):
    yield NoteFactory.create(owner=user)
