from django.test import TestCase

from django.contrib.auth import get_user_model

user_model = get_user_model()


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test Creating a new user with an email is successful"""
        email = "test@test.com"
        password = "test@1234"
        first_name = "test"
        last_name = "user"
        user = user_model.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_user_email_normalized(self):
        """Test Creating a new user with an email is successful"""
        email = "test@tESt.com"
        password = "test@1234"
        first_name = "test"
        last_name = "user"
        user = user_model.objects.create_user(
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
        user = get_user_model().objects.create_superuser(
            "test@test.com",
            "123",
            first_name="admin",
            last_name="user"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
