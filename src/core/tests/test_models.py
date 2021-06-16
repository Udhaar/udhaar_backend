from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from ..models import User, Transaction, OutstandingBalance, Notification

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

    def test_transaction_string(self):
        payer = user_model.objects.create_user(
            email="payer@gmail.com",
            password="Payer@123",
            first_name="PayerF",
            last_name="PayerL",
        )
        receiver = user_model.objects.create_user(
            email="receiver@gmail.com",
            password="Receiver@123",
            first_name="ReceiverF",
            last_name="ReceiverL",
        )

        transaction = Transaction.objects.create(
            payer=payer,
            receiver=receiver,
            created_by=payer,
            amount=10.00,
            message="First transaction"
        )

        self.assertEqual(
            str(transaction),
            "Transaction PayerF PayerL => ReceiverF ReceiverL : 10.00"
        )

    def test_outstanding_balance_string(self):
        payer = user_model.objects.create_user(
            email="payer@gmail.com",
            password="Payer@123",
            first_name="PayerF",
            last_name="PayerL",
        )
        receiver = user_model.objects.create_user(
            email="receiver@gmail.com",
            password="Receiver@123",
            first_name="ReceiverF",
            last_name="ReceiverL",
        )

        outstanding_balance = OutstandingBalance.objects.create(
            payer=payer,
            receiver=receiver,
            balance=10.00
        )

        self.assertEqual(
            "receiver@gmail.com owes payer@gmail.com : 10.00",
            str(outstanding_balance)
        )

    def test_notification_string(self):
        user = user_model.objects.create_user(
            email="user@gmail.com",
            password="User@123",
            first_name="UserF",
            last_name="UserL",
        )
        message = "message : Paid 10 rs."

        notification = Notification.objects.create(
            user=user,
            message=message
        )
        self.assertEqual(
            "user@gmail.com message : Paid 10 rs. false",
            str(notification)
        )