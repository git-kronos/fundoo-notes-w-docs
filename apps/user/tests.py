from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from apps.utils.factory import UserFactory

fake = Faker()


# Create your tests here.
class URLs:
    register = reverse("user:register")
    login = reverse("user:login")
    profile = reverse("user:profile")


class TestUser(TestCase):
    def test_register_api(self):
        """test with different combinations of payload value"""
        parameters = (
            ({"email": fake.email(), "password": fake.password()}, 201),
            ({"email": "", "password": fake.password()}, 400),
            ({"email": fake.email(), "password": ""}, 400),
            ({"email": fake.name(), "password": fake.password()}, 400),
            ({"email": fake.name(), "password": fake.word()}, 400),
        )
        for param in parameters:
            res = self.client.post(URLs.register, data=param[0], content_type="application/json")
            assert res.status_code == param[1]

    def test_password_in_register_api(self):
        """test with variations of payload"""
        email = fake.email()
        gen_payload = lambda passd: {"email": email, "password": passd}

        parameters = (
            (gen_payload("password"), 400),
            (gen_payload("PASSWORD"), 400),
            (gen_payload("PassWo1"), 400),
            (gen_payload("Password1"), 201),
        )
        for param in parameters:
            res = self.client.post(URLs.register, data=param[0], content_type="application/json")
            self.assertEqual(res.status_code, param[1])

    def test_password_not_in_response(self):
        """test with password like sensitive info not exposed in response"""
        payload = {"email": fake.email(), "password": fake.password()}
        response = self.client.post(URLs.register, data=payload, content_type="application/json")
        self.assertNotIn("password", response.json())

    def test_password_stored_in_database_is_not_raw_password(self):
        """test with password like sensitive info not exposed in response"""
        raw_password = fake.password()
        payload = {"email": fake.email(), "password": raw_password}
        self.client.post(URLs.register, data=payload, content_type="application/json")

        obj = get_user_model().objects.first()
        self.assertNotEqual(obj.password, raw_password)  # type: ignore
        self.assertTrue(obj.check_password(raw_password))  # type: ignore

    def test_login_api(self):
        """Login api with credentials"""
        params = (
            ({"email": fake.email(), "password": fake.password()}, 202),
            ({"email": "", "password": fake.password()}, 400),
            ({"email": fake.email(), "password": ""}, 400),
            ({"email": fake.name(), "password": fake.password()}, 400),
            ({"email": fake.name(), "password": fake.word()}, 400),
        )
        for param in params:
            UserFactory.create(**param[0])
            response = self.client.post(URLs.login, data=param[0])
            self.assertEqual(response.status_code, param[1])

    def test_login_api_response_have_auth_token(self):
        """Login api with credentials"""
        raw_password = fake.password()
        obj = UserFactory.create(password=raw_password)
        response = self.client.post(URLs.login, data={"email": obj.email, "password": raw_password})
        self.assertIn("token", response.json())

    def test_profile_api_without_authentication(self):
        """Login api with credentials"""
        response = self.client.get(URLs.profile)
        self.assertEqual(response.status_code, 403)

    def test_profile_api_with_authentication(self):
        """Login api with credentials"""
        obj = UserFactory.create()
        response = self.client.get(URLs.profile, HTTP_AUTHORIZATION=f"Bearer {obj.token}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.json())
