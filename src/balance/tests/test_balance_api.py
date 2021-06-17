from rest_framework.test import APIClient
from django.test import TestCase
from core.models import Transaction, User
from django.urls import reverse
from rest_framework import status

BALANCE_LIST_URL = reverse("balance:balance_list")


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
        self.user3 = User.objects.create(
            email="user3@gmail.com",
            password="User3@123",
            first_name="User3F",
            last_name="User3L",
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
        self.transaction3 = Transaction.objects.create(
            payer=self.user1,
            receiver=self.user3,
            created_by=self.user1,
            amount=20.0,
            message="First Transaction"
        )
        self.transaction4 = Transaction.objects.create(
            payer=self.user2,
            receiver=self.user3,
            created_by=self.user2,
            amount=25.0,
            message="First Transaction"
        )

    def test_list_balances_user1(self):
        self.transaction1.accept()
        self.transaction2.accept()
        self.transaction3.accept()

        self.client.force_authenticate(self.user1)

        res = self.client.get(BALANCE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data["results"]), 2)
        self.assertEqual(
            res.data["results"][0]["user"]["external_id"],
            str(self.user3.external_id)
        )
        self.assertEqual(res.data["results"][0]["balance"], "20.00")
        self.assertEqual(res.data["results"][1]["user"]
                         ["external_id"], str(self.user2.external_id))
        self.assertEqual(res.data["results"][1]["balance"], "4.00")
