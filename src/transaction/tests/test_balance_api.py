from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Transaction, User
from django.urls import reverse
from rest_framework import status


def balance_url(user):
    return reverse("balance:get_balance", args=[user.external_id])


class BalanceApiTests(TestCase):
    def setUp(self) -> None:
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
        self.transaction1 = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user2,
            created_by=self.user1,
            amount=14.0,
            message="First Transaction"
        )
        self.transaction2 = Transaction.objects.create(
            payer=self.user2,
            receiver=self.user1,
            created_by=self.user1,
            amount=10.0,
            message="First Transaction"
        )

    def test_accept_transaction_balance(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(balance_url(self.user2))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"balance": 0.0})

        self.transaction1.accept()
        res = self.client.get(balance_url(self.user2))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"balance": 14.0})

        self.client.force_authenticate(self.user2)
        res = self.client.get(balance_url(self.user1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"balance": -14.0})

        self.transaction2.accept()
        self.client.force_authenticate(self.user1)
        res = self.client.get(balance_url(self.user2))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"balance": 4.0})

        self.client.force_authenticate(self.user2)
        res = self.client.get(balance_url(self.user1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {"balance": -4.0})
