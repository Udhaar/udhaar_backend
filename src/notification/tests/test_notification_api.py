from django.test import TestCase
from rest_framework.test import APIClient
from core.models import (
    Transaction,
    User,
    Notification
)
from django.urls import reverse
from rest_framework import status

NOTIFICATION_LIST_URL = reverse("notification:notification-list")


def notification_url(notification):
    return reverse(
        "notification:notification-detail",
        args=[str(notification.external_id)]
    )


class NotificationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.transaction1 = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user1,
            amount=10.00,
            message="First transaction"
        )
        self.transaction2 = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user1,
            amount=10.00,
            message="First transaction"
        )
        self.transaction3 = Transaction.objects.create(
            payer=self.user3,
            receiver=self.user4,
            created_by=self.user3,
            amount=10.00,
            message="First transaction"
        )

    def test_list_notification(self):
        self.client.force_authenticate(self.user2)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        for notification in res.data["results"]:
            self.assertEqual(
                notification["notification_type"], "NEW_RECEIVED_TRANSACTION"
            )

    def test_list_notification_accept(self):
        self.transaction1.accept()
        self.client.force_authenticate(self.user2)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        self.client.force_authenticate(self.user1)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(
            res.data["results"][0]["notification_type"],
            "ACCEPTED_TRANSACTION"
        )

    def test_list_notification_decline(self):
        self.transaction2.decline("Not correct")
        self.client.force_authenticate(self.user2)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        self.client.force_authenticate(self.user1)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(
            res.data["results"][0]["notification_type"],
            "DECLINED_TRANSACTION"
        )

    def test_dismiss_notification(self):
        self.client.force_authenticate(self.user2)
        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(len(res.data["results"]), 2)

        notification: Notification = Notification.objects.filter(
            user=self.user2
        ).first()
        self.assertIsNotNone(notification)

        res = self.client.delete(notification_url(notification))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(NOTIFICATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
