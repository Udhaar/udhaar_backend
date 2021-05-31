from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import User

user_model: User = get_user_model()
CREATE_USER_URL = reverse("user:create")


def make_user(**kwargs):
    return user_model.objects.create_user(
        last_name="lname",
        first_name="fname",
        **kwargs,
    )


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            "email": "admin@test.com",
            "password": "password@123",
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
