"""
-  All auto genereted values can be changed by assigning a custom value at build
i.e

```python

obj: User = AdminFactory.build(password="hello")
print(obj.check_password("Password@12"))    # False
print(obj.check_password("hello"))          # True
```
but

```python
obj: User = AdminFactory.build()
print(obj.check_password("Password@12"))    # True
print(obj.check_password("hello"))          # False
```
"""
import factory
from django.contrib.auth.hashers import make_password

from apps.note.models import Note
from apps.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # email = factory.Faker("email")  # nb_words=4
    email = factory.LazyAttribute(
        lambda a: "{}.{}@example.com".format(a.first_name, a.last_name).lower()
    )
    password = factory.PostGenerationMethodCall("set_password", "Password@12")
    # here `Password@12` is default value.
    # password = factory.LazyFunction(lambda: make_password("Password@12"))

    is_superuser = False
    is_staff = True
    is_active = True


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Faker("sentence", nb_words=4)
    body = factory.Faker("sentence", nb_words=10)
    owner = factory.SubFactory(UserFactory)
    # owner = factory.RelatedFactory(AdminFactory, "owner", visited=True)
