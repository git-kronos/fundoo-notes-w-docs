import pytest
from django.urls import reverse
from faker import Faker

from apps.note.models import Note
from apps.utils.factory import NoteFactory, UserFactory

fake = Faker()

get_headers = lambda user: {
    "HTTP_AUTHORIZATION": f"Bearer {user.token}",
    "content_type": "application/json",
}

sentenceN = lambda n: fake.sentence(nb_words=n)
sentence = lambda: fake.sentence()


class URLs:
    list = reverse("note:note-list")
    detail = lambda pk: reverse("note:note-detail", kwargs={"pk": pk})
    collab = lambda user_id: reverse(
        "note:note-collab", kwargs={"pk": user_id}
    )
    user = reverse("note:note-user")


@pytest.mark.django_db
class TestNote:
    @pytest.mark.parametrize(
        "payload,status_code",
        [
            ({"title": sentence(), "body": sentence()}, 201),
            ({"title": "", "body": sentence()}, 400),  # without title
            ({"title": sentenceN(4), "body": ""}, 400),  # without body
        ],
    )
    def test_note_create_api(self, client, user, payload, status_code):
        """Test create note api with auth token"""

        response = client.post(URLs.list, data=payload, **get_headers(user))
        assert response.status_code == status_code

    @pytest.mark.testing
    def test_note_list_api(self, client, user):
        """Test list note api with auth token"""
        NoteFactory.create_batch(2, owner=user)  # notes of current user
        response = client.get(URLs.list, **get_headers(user))
        assert len(response.json()["data"]["results"]) == 2
        assert response.status_code == 200

    def test_note_list_returns_only_current_users_data(self, client, user):
        """Test if list note api response shows only authorised user's note's or not!"""
        NoteFactory.create_batch(2)  # notes of random users
        response = client.get(URLs.list, **get_headers(user))
        assert len(response.json()["data"]["results"]) == 0
        assert response.status_code == 200

    def test_note_retrieve_with_auth(self, client, user):
        """Note retrieve api with auth"""
        obj = NoteFactory.create(owner=user)  # notes of random users
        response = client.get(URLs.detail(obj.id), **get_headers(user))
        assert response.status_code == 200
        assert response.json()["data"]["id"] == obj.id
        assert response.json()["data"]["owner"] == user.id

    def test_note_retrieve_without_auth(self, client, user):
        """Note retrieve api with auth"""
        obj = NoteFactory.create(owner=user)  # notes of random users
        response = client.get(URLs.detail(obj.id))
        assert response.status_code == 403

    def test_note_update_without_auth(self, client, user):
        """Note update api with auth"""
        payload = {"title": sentenceN(5), "body": sentence}
        obj = NoteFactory.create(owner=user)  # notes of random users
        response = client.put(URLs.detail(obj.id), data=payload)
        assert response.status_code == 403

    def test_note_update_with_auth(self, client, user):
        payload = {"title": sentenceN(5), "body": sentence()}
        obj = NoteFactory.create(owner=user)
        response = client.put(
            URLs.detail(obj.id), data=payload, **get_headers(user)
        )
        post_action = Note.objects.get(pk=obj.pk)
        print(response.json())
        result = response.json()["data"]
        assert obj.title != result["title"]
        assert post_action.title == result["title"]
        assert response.status_code in [200, 202]

    def test_note_delete_with_auth(self, client, user):
        obj = NoteFactory.create(owner=user)
        response = client.delete(URLs.detail(obj.id), **get_headers(user))
        post_action = Note.objects.all()
        assert not post_action.exists()
        assert response.status_code == 204

    def test_note_delete_without_auth(self, client, user):
        obj = NoteFactory.create(owner=user)
        headers = get_headers(user)
        headers.pop("HTTP_AUTHORIZATION")
        response = client.delete(URLs.detail(obj.id), **headers)
        post_action = Note.objects.all()
        assert post_action.exists()
        assert response.status_code == 403

    def test_delete_note_of_other_user(self, client, user):
        NoteFactory.create(owner=user)
        obj = NoteFactory.create()
        response = client.delete(URLs.detail(obj.id), **get_headers(user))
        post_action = Note.objects.filter(owner=user)
        assert post_action.exists()
        assert response.status_code == 404

    def test_collaborator_create_api(self, client, user):
        notes: list[Note] = NoteFactory.create_batch(size=2, owner=user)
        note: Note = notes[0]
        users = [user.id for user in UserFactory.create_batch(size=1)]

        assert (
            note.collaborator.count() == 0
        )  # collaborator count before api call
        response = client.post(
            URLs.collab(note.pk),
            data={"collaborator": users},
            **get_headers(user),
        )
        assert response.status_code == 202
        obj = Note.objects.get(pk=note.pk)
        assert (
            obj.collaborator.count() == 1
        )  # collaborator count after api call
        assert (
            obj.collaborator.first().id == users[0]
        )  # checking if collaborator in db is same user that created above

    def test_collaborator_delete_api(self, client, user):
        notes = NoteFactory.create_batch(size=2, owner=user)
        note = notes[0]
        users = [user.id for user in UserFactory.create_batch(size=3)]
        note.collaborator.set(users)

        assert (
            note.collaborator.count() == 3
        )  # collaborator count before api call
        response = client.delete(
            URLs.collab(note.pk),
            data={"collaborator": users},
            **get_headers(user),
        )
        assert response.status_code == 202  # checking api call was successful
        obj = Note.objects.get(pk=note.pk)
        assert (
            obj.collaborator.count() == 0
        )  # collaborator count after api call
