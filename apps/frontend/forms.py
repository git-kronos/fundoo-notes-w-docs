from dataclasses import field

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from apps.note.models import Note

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "password")
        widgets = {"password": forms.PasswordInput}
        help_texts = {
            "email": "<li>user@email.com</li>",
            "password": password_validation.password_validators_help_text_html(),
        }


class NoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        # Additional step to add custom parameter(user) to Form instance
        self.user = kwargs.pop("user", None)
        user_id = getattr(self.user, "id")
        assert isinstance(user_id, int)
        super().__init__(*args, **kwargs)

        # manipulate each field...
        self.fields["owner"].queryset = User.objects.filter(id=user_id)
        self.fields["owner"].initial = user_id

        qs = self.fields["collaborator"].queryset
        self.fields["collaborator"].queryset = qs.exclude(id=user_id)
        self.fields["collaborator"].required = False

    def clean_collaborator(self):
        """individual validation"""
        data = self.cleaned_data["collaborator"]
        if self.user in data:
            raise ValidationError(
                "%(user)s cann't be a collaborator" % {"user": self.user.id},
            )
        return data

    class Meta:
        model = Note
        fields = ("title", "body", "owner", "collaborator")

    #     labels = {"name": "Writer"}
    #     help_texts = {"name": "Some useful help text."}
    #     error_messages = {
    #         "name": {"max_length": "This writer's name is too long."}
    #     }
    #     field_classes = {"slug": MySlugFormField}
    #     localized_fields = ["birth_date"]
    #     exclude = ["body"]

    # def clean(self):
    #     # common validation
    #     cleaned_data = super().clean()
    #     if cleaned_data:
    #         raise ValidationError("testing error", code="error")
    #     return cleaned_data
