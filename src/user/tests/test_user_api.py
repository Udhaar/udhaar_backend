from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import User
from user.serializers import UserSerializer

user_model: User = get_user_model()
CREATE_USER_URL = reverse("user:create")
CREATE_TOKEN_URL = reverse("user:token")
USER_SEARCH_URL = reverse("user:search")
USER_URL = reverse("user:me")


def make_user(first_name="fname", last_name="lname", **kwargs):
    return user_model.objects.create_user(
        last_name=last_name,
        first_name=first_name,
        **kwargs,
    )


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            "email": "admin@test.com",
            "password": "Password@123",
            "first_name": "fname",
            "last_name": "lname",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = user_model.objects.get(external_id=res.data["external_id"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)
        self.assertIn("external_id", res.data)
        self.assertEqual(res.data["first_name"], payload["first_name"])
        self.assertEqual(res.data["last_name"], payload["last_name"])

    def test_user_exists(self):
        """Text creating user with email that already exists"""
        payload = {
            "email": "admin@test.com",
            "password": "password@123",
        }
        make_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_password_without_number(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@Test",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_password_without_uppercase(self):
        payload = {
            "email": "test_short@test.com",
            "password": "Test12345",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_password_without_symbol(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@Test",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@123",
        }
        make_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_invalid_credentials(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@123",
        }
        make_user(**payload)
        payload["password"] = "wrong password"
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_no_user(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@123",
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_missing_field(self):
        payload = {
            "email": "test_short@test.com",
            "password": "test@123",
        }
        make_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL, {"email": payload["email"]})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(USER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = make_user(first_name="testfirst", last_name="testlast",
                              email="admin@test.com", password="admin123")
        self.user.refresh_from_db()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(USER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["first_name"], self.user.first_name)
        self.assertEqual(res.data["last_name"], self.user.last_name)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["external_id"], str(self.user.external_id))

    def test_post_me_not_allowed(self):
        res = self.client.post(USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {
            "first_name": "newfirstname",
            "last_name": "newlastname",
            "password": "New@pass12"
        }

        res = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payload["first_name"], self.user.first_name)
        self.assertEqual(payload["last_name"], self.user.last_name)
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_update_user_email_fails(self):
        old_email = self.user.email
        payload = {
            "email": "something@email.com",
        }

        res = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, old_email)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_search_success(self):
        user1 = make_user(first_name="testfirst", last_name="testlast",
                          email="user@test.com", password="User@123")
        res = self.client.get(
            f"{USER_SEARCH_URL}?email=user@test.com"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, UserSerializer(user1).data)

    def test_user_search_not_found(self):
        res = self.client.get(
            f"{USER_SEARCH_URL}?email=usernotexist@test.com"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_search_self_not_found(self):
        res = self.client.get(
            f"{USER_SEARCH_URL}?email=admin@test.com"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
