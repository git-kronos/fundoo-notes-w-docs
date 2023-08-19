from django import forms
from django.contrib import admin

from apps.note.models import Note
from apps.user.models import User


class NoteForm(forms.ModelForm):
    collaborator = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by("-id"),
        required=False,
    )

    class Meta:
        model = Note
        fields = ("title", "body", "owner", "collaborator")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    form = NoteForm
    list_display = ("id", "title", "owner_id")
    ordering = ("-id",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_superuser")
    ordering = ("-id",)
