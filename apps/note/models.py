from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="notes",
    )
    collaborator = models.ManyToManyField("user.User", related_name="collab")

    class Meta:
        db_table = "note"

    def __str__(self) -> str:
        return "Note(id=%d, owner_id=%d)" % (self.id, self.owner_id)
