from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from ..models import User

user_model: User = get_user_model()


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = user_model.objects.create_superuser(
            "admin@test.com",
            "password@123",
            first_name="admin",
            last_name="user",
        )
        self.client.force_login(self.admin_user)
        self.user = user_model.objects.create_user(
            "test@test.com",
            "pass@123",
            first_name="user",
            last_name="user",
        )

    def test_users_listed(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.last_name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
