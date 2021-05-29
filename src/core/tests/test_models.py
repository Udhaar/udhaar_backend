from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from datetime import datetime
from ..models import User

user_model = get_user_model()
test_date = datetime.now()


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test Creating a new user with an email is successful"""
        email = "test@test.com"
        password = "test@1234"
        first_name = "test"
        last_name = "user"
        user: User = user_model.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertIsNotNone(user.created_date)
        self.assertTrue(user.check_password(password))

    def test_create_user_email_normalized(self):
        """Test Creating a new user with an email is successful"""
        email = "test@tESt.com"
        password = "test@1234"
        first_name = "test"
        last_name = "user"
        user: User = user_model.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.assertEqual(user.email, email.lower())
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "123")

    def test_create_new_superuser(self):
        user: User = get_user_model().objects.create_superuser(
            "test@test.com",
            "123",
            first_name="admin",
            last_name="user"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_last_modified_date(self):
        password = "test@1234"
        email = "test@tESt.com"
        first_name = "test"
        last_name = "user"
        user: User = user_model.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.save()
        self.assertIsNotNone(user.last_modified_date)
        modified_date = user.last_modified_date
        user.first_name = "test2"
        user.save()
        self.assertGreater(user.last_modified_date, modified_date)
