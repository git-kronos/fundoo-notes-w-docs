from django.contrib.auth import get_user_model
from drf_yasg import openapi
from rest_framework import serializers

from apps.note.models import Note

User = get_user_model()

"""
https://www.django-rest-framework.org/api-guide/serializers/

Serializers are used to `R`ead, `C`reate, `U`pdate table row

End result will be enresult will be a serializer object.

`serializer_object.data` carries model info in dict format

"""


class NoteResponseSerializer(serializers.ModelSerializer):
    class Meta:
        swagger_schema_fields = {"title": "NoteOut"}
        model = Note
        fields = "__all__"


class NoteSerializer(serializers.ModelSerializer):

    """
    ```python
    class Meta:
        model = ModelClass
        fields = [ selective/all fields... ] or '__all__'
        read_only_fields = () # list of fileds not required in creating object
        extra_kwargs = {} # used to provide extra config to each field


        exclude = [] # `list[str]`/`tuple[str...]` of all exclude fields. used alternative of fields
        depth = int value
    ```
    """

    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "Note",
            "required": ["title", "body"],
            "properties": {
                "title": openapi.Schema(
                    title="Email subject", type=openapi.TYPE_STRING
                ),
                "body": openapi.Schema(
                    title="Email body", type=openapi.TYPE_STRING
                ),
            },
        }
        model = Note
        fields = "__all__"
        extra_kwargs = {"id": {"read_only": True}}

    def validate_title(self, value):
        """
        method_name = validate_(field_name)
        """
        if not isinstance(value, str):
            raise serializers.ValidationError("srt value")
        return value

    # below methods can be used to do perform manual logic

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    # def update(self, instance, validated_data):
    #     return super().update(instance, validated_data)


"""
create(), update() are optional in ModelSerializer derivativs

but in case of custom serializer(`Serializer`) to perform table update operattion i.e. `serializer_instance.save()`, it is mandatory to define create() and update()

For data retrieve these methods and validation logics are not needed.

Alternative code:

class NoteCustomSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_title(self, v):
        # title field validation
        return v

    def validate_body(self, v):
        # title field validation
        return v

    def validate(self, attrs):
        # attr is a dictonary of all all fields and there values
        # i.e attr = {'title': user_input, 'body': user_input, 'owner': user_object}

        # owner field's value will be an object verified by PrimaryKeyRelatedField()

        # this method a shortcut/alternative of targeted field validation(like above).
        return attrs

    def create(self, validated_data):
        # validated_data = {'title': user_input, 'body': user_input, 'owner': user_object}
        obj = Note.objects.create(**validated_data)
        return obj

    def update(self, instance, validated_data: dict):
        # instance = note instance. this value is provided in the view to the serializer instance
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
"""


class ProfileNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "title", "body")
        # Both `fields` and `exclude` can't be set simultaniously


class ProfileSerializer(serializers.ModelSerializer):
    notes = ProfileNoteSerializer(source="note_set", many=True, read_only=True)
    """
    notes = serializers.SerializerMethodField(method_name="get_notes")

        def get_notes(self, instance: Profile):
            return [_.pk for _ in instance.notes]
    """

    class Meta:
        swagger_schema_fields = {"title": "NoteByUser"}
        model = User
        fields = ("id", "email", "notes")
