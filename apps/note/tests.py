from django.test import TestCase
from django.urls import reverse
from faker import Faker

from apps.note.models import Note
from apps.utils.factory import NoteFactory, UserFactory

fake = Faker()


sentenceN = lambda n: fake.sentence(nb_words=n)
sentence = lambda: fake.sentence()


# Create your tests here.
class URLs:
    list = reverse("note:note-list")
    detail = lambda pk: reverse("note:note-detail", kwargs={"pk": pk})
    collab = lambda user_id: reverse("note:collab-note", kwargs={"pk": user_id})
    # user = reverse("note:note-user")


class TestNote(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.user.token}", "content_type": "application/json"}
        return super().setUp()

    def test_note_create_api(self):
        parameters = (
            ({"title": sentence(), "body": sentenceN(4)}, 201),
            ({"title": "", "body": sentenceN(4)}, 400),
            ({"title": sentence(), "body": ""}, 400),
        )

        """Test create note api with auth token"""
        for parameter in parameters:
            response = self.client.post(URLs.list, data=parameter[0], **self.headers)  # type: ignore
            self.assertEqual(response.status_code, parameter[1])

    def test_note_list_api(self):
        """Test list note api with auth token"""
        NoteFactory.create_batch(2, owner=self.user)
        response = self.client.get(URLs.list, **self.headers)  # type: ignore
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.status_code, 200)

    def test_note_list_returns_only_current_users_data(self):
        """Test if list note api response shows only authorised user's note's or not!"""
        NoteFactory.create_batch(2)  # notes of random users
        response = self.client.get(URLs.list, **self.headers)  # type: ignore
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.status_code, 200)

    def test_note_retrieve_with_auth(self):
        """Note retrieve api with auth"""
        obj = NoteFactory.create(owner=self.user)
        response = self.client.get(URLs.detail(obj.id), **self.headers)  # type: ignore
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], obj.id)
        self.assertEqual(response.json()["owner"], self.user.id)

    def test_note_retrieve_without_auth(self):
        """Note retrieve api with auth"""
        obj = NoteFactory.create(owner=self.user)
        response = self.client.get(URLs.detail(obj.id))
        self.assertEqual(response.status_code, 403)

    def test_note_update_without_auth(self):
        """Note update api with auth"""
        payload = {"title": sentenceN(5), "body": sentence}
        obj = NoteFactory.create(owner=self.user)
        response = self.client.put(URLs.detail(obj.id), data=payload)
        self.assertEqual(response.status_code, 403)

    def test_note_update_with_auth(self):
        payload = {"title": sentenceN(5), "body": sentence()}
        obj = NoteFactory.create(owner=self.user)
        response = self.client.put(URLs.detail(pk=obj.id), data=payload, **self.headers)  # type: ignore
        post_action = Note.objects.get(pk=obj.id)
        result = response.json()
        self.assertNotEqual(obj.title, result["title"])
        self.assertEqual(post_action.title, result["title"])
        self.assertIn(response.status_code, [200, 202])

    def test_note_delete_with_auth(self):
        obj = NoteFactory.create(owner=self.user)
        response = self.client.delete(URLs.detail(obj.id), **self.headers)  # type: ignore
        post_action = Note.objects.all()
        self.assertFalse(post_action.exists())
        self.assertEqual(response.status_code, 204)

    def test_note_delete_without_auth(self):
        obj = NoteFactory.create(owner=self.user)
        self.headers.pop("HTTP_AUTHORIZATION")
        response = self.client.delete(URLs.detail(obj.id), **self.headers)  # type: ignore
        post_action = Note.objects.all()
        self.assertTrue(post_action.exists())
        self.assertEqual(response.status_code, 403)

    def test_delete_note_of_other_user(self):
        NoteFactory.create(owner=self.user)
        obj = NoteFactory.create()
        response = self.client.delete(URLs.detail(obj.id), **self.headers)  # type: ignore
        post_action = Note.objects.filter(owner=self.user)
        self.assertTrue(post_action.exists())
        self.assertEqual(response.status_code, 404)

    def test_collaborator_create_api(self):
        notes: list[Note] = NoteFactory.create_batch(size=2, owner=self.user)
        note: Note = notes[0]

        users = [user.id for user in UserFactory.create_batch(size=1)]

        self.assertEqual(note.collaborator.count(), 0)
        response = self.client.post(URLs.collab(note.pk), data={"collaborator": users}, **self.headers)  # type: ignore
        self.assertEqual(response.status_code, 202)
        obj = Note.objects.get(pk=note.pk)
        self.assertEqual(obj.collaborator.count(), 1)
        self.assertEqual(obj.collaborator.first().id, users[0])  # type: ignore

    def test_collaborator_delete_api(self):
        notes = NoteFactory.create_batch(size=2, owner=self.user)
        note = notes[0]
        users = [user.id for user in UserFactory.create_batch(size=3)]
        note.collaborator.set(users)

        self.assertEqual(note.collaborator.count(), 3)
        response = self.client.delete(URLs.collab(note.pk), data={"collaborator": users}, **self.headers)  # type: ignore
        self.assertEqual(response.status_code, 202)
        obj = Note.objects.get(pk=note.pk)
        self.assertEqual(obj.collaborator.count(), 0)
