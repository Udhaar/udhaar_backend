from django.test import TestCase
from ..models import Notification, NotificationTypeChoices, User, Transaction


class NotificationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            email="user1@gmail.com",
            password="User1@123",
            first_name="User1F",
            last_name="User1L",
        )
        self.user2 = User.objects.create(
            email="user2@gmail.com",
            password="User2@123",
            first_name="User2F",
            last_name="User2L",
        )
        self.user3 = User.objects.create(
            email="User3@gmail.com",
            password="User3@123",
            first_name="User3F",
            last_name="User3l",
        )
        self.user4 = User.objects.create(
            email="User4@gmail.com",
            password="User4@123",
            first_name="User4F",
            last_name="User4L",
        )
        self.transaction3 = Transaction.objects.create(
            payer=self.user3,
            receiver=self.user4,
            created_by=self.user3,
            amount=10.00,
            message="First transaction"
        )

    def test_notification_received(self):
        transaction = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user1,
            amount=10.00,
            message="First transaction"
        )
        notification = Notification.objects.filter(user=self.user2).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.transaction, transaction)
        self.assertEqual(
            notification.notification_type,
            NotificationTypeChoices.NEW_RECEIVED_TRANSACTION.value
        )
        self.assertFalse(notification.is_dismissed)

    def test_notification_sent(self):
        transaction = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user2,
            amount=10.00,
            message="First transaction"
        )
        notification = Notification.objects.filter(user=self.user1).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.transaction, transaction)
        self.assertEqual(notification.notification_type,
                         NotificationTypeChoices.NEW_SENT_TRANSACTION.value)
        self.assertFalse(notification.is_dismissed)

    def test_notification_accept(self):
        transaction = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user1,
            amount=10.00,
            message="First transaction"
        )
        transaction.accept()
        notification = Notification.objects.filter(user=self.user1).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.transaction, transaction)
        self.assertEqual(notification.notification_type,
                         NotificationTypeChoices.ACCEPTED_TRANSACTION.value)
        self.assertFalse(notification.is_dismissed)

    def test_notification_decline(self):
        transaction = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user2,
            amount=10.00,
            message="First transaction"
        )
        transaction.decline("I don't know")
        notification = Notification.objects.filter(user=self.user2).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.transaction, transaction)
        self.assertEqual(notification.notification_type,
                         NotificationTypeChoices.DECLINED_TRANSACTION.value)
        self.assertFalse(notification.is_dismissed)
