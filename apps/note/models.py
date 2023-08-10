from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class Profile(User):
    """
    Proxy table:
        Include additional feature without creating separate table in database
    """

    @property
    def notes(self):
        """
        self.note_set.all():
            reverse relation ship. Only works in ForeignKey() related field.
            result: all notes of the targeted user
        """
        return self.note_set.all()

    class Meta:
        proxy = True


class Note(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Meta:
        db_table = "note"

    def __str__(self) -> str:
        return "Note(%d, %s)" % (self.id, self.title)
