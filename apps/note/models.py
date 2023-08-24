from django.db import models

Q = models.Q


class NoteQuerySet(models.QuerySet):
    def owner_notes(self, owner=None):
        if owner is None or owner == "":
            return self.none()
        lookups = Q(owner=owner) | Q(collaborator=owner)
        return self.prefetch_related("collaborator", "owner").filter(lookups)


class NoteManager(models.Manager):
    def get_queryset(self):
        return NoteQuerySet(model=self.model, using=self._db)

    def owner_notes(self, owner=None):
        return self.get_queryset().owner_notes(owner=owner)


class Note(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="notes")
    collaborator = models.ManyToManyField("user.User", related_name="collab")
    objects = NoteManager()

    class Meta:
        db_table = "note"
        ordering = ["-id"]
