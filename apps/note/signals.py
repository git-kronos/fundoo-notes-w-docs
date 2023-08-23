from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.note.models import Note
from apps.utils import collaborator_signals


@receiver(m2m_changed, sender=Note.collaborator.through)
def check_many2many_signal(sender, action: str, **kwargs):
    """
    action: pre_add, post_add, pre_remove, post_remove
    """
    if action == "post_add":
        print(f"{sender.__name__} collaborator done")
        print("-------------------------------------------------")


@receiver(collaborator_signals)
def collaborator_action(signal, payload, **kwargs):
    collab: list = list(map(str, payload.get("data")["collaborator"]))
    action: str = payload.get("action")
    if bool(collab):
        c = ",".join(collab)
        print("*************************")
        print(f"{action.upper()} collaborator: User ids `{c}`")
        print("*************************")
