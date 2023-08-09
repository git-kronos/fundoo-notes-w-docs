from django.db import models


# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Meta:
        db_table = "note"

    def __str__(self) -> str:
        return "Note(%d, %s)" % (self.id, self.title)
