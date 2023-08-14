import pytest
from django.urls import reverse
from faker import Faker

from apps.utils.factory import UserFactory

fake = Faker()


class URLs:
    register = reverse("user:register")
    login = reverse("user:login")
    profile = reverse("user:profile")


@pytest.mark.django_db
class TestUser:
    @pytest.mark.parametrize(
        "payload,status_code",
        [
            (
                {"email": fake.email(), "password": fake.password()},
                201,
            ),  # right combination
            ({"email": "", "password": fake.password()}, 400),  # without email
            ({"email": fake.email(), "password": ""}, 400),  # without password
            (
                {"email": fake.name(), "password": fake.password()},
                400,
            ),  # if not a email
            (
                {"email": fake.name(), "password": fake.word()},
                400,
            ),  # if password not a valid password
        ],
    )
    def test_register_api(self, client, payload, status_code):
        """test with different combinations of payload value"""
        res = client.post(
            URLs.register, data=payload, content_type="application/json"
        )
        assert res.status_code == status_code

    @pytest.mark.parametrize(
        "payload,status_code",
        [
            (
                {"email": fake.email(), "password": "password"},
                400,
            ),  # only lowercase
            (
                {"email": fake.email(), "password": "PASSWORD"},
                400,
            ),  # only upper case
            (
                {"email": fake.email(), "password": "PassWo1"},
                400,
            ),  # less than 8
            (
                {"email": fake.email(), "password": "Password1"},
                201,
            ),  # acceptable password(1 upper, 1 lower, 1 number)
        ],
    )
    def test_password_in_register_api(self, client, payload, status_code):
        """test with variations of payload"""
        res = client.post(
            URLs.register, data=payload, content_type="application/json"
        )
        assert res.status_code == status_code

    def test_password_not_in_response(self, client):
        """test with password like sensitive info not exposed in response"""
        payload = {"email": fake.email(), "password": fake.password()}
        response = client.post(
            URLs.register, data=payload, content_type="application/json"
        )
        assert "password" not in response.json()

    def test_password_stored_in_database_is_not_raw_password(
        self, client, django_user_model
    ):
        """test with password like sensitive info not exposed in response"""
        raw_password = fake.password()
        payload = {"email": fake.email(), "password": raw_password}
        client.post(
            URLs.register, data=payload, content_type="application/json"
        )

        obj = django_user_model.objects.first()
        assert obj.password != raw_password
        assert obj.check_password(raw_password)

    @pytest.mark.parametrize(
        "credentials,status_code",
        [
            (
                {"email": fake.email(), "password": fake.password()},
                202,
            ),  # right combination
            ({"email": "", "password": fake.password()}, 400),  # without email
            ({"email": fake.email(), "password": ""}, 400),  # without password
            (
                {"email": fake.name(), "password": fake.password()},
                400,
            ),  # if email not a email
            (
                {"email": fake.name(), "password": fake.word()},
                400,
            ),  # if password not a valid password
        ],
    )
    def test_login_api(self, client, credentials, status_code):
        """Login api with credentials"""
        UserFactory.create(**credentials)
        response = client.post(URLs.login, data=credentials)
        assert response.status_code == status_code

    def test_login_api_response_have_auth_token(
        self, django_user_model, client
    ):
        """Login api with credentials"""
        raw_password = fake.password()
        obj = UserFactory.create(password=raw_password)
        response = client.post(
            URLs.login, data={"email": obj.email, "password": raw_password}
        )
        assert "token" in response.json()

    def test_profile_api_without_authentication(self, client):
        """Login api with credentials"""
        response = client.get(URLs.profile)
        assert response.status_code == 403

    def test_profile_api_with_authentication(self, client):
        """Login api with credentials"""
        obj = UserFactory.create()
        response = client.get(
            URLs.profile, HTTP_AUTHORIZATION=f"Bearer {obj.token}"
        )
        assert response.status_code == 200
        assert "password" not in response.json()
