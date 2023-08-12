from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        db_table = "note"

    def __str__(self) -> str:
        return "Note(%d, %s)" % (self.id, self.title)
