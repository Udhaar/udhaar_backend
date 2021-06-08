from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Transaction, User
from django.urls import reverse
from rest_framework import status

from transaction.serializers import TransactionSerializer

TRANSACTION_URL = reverse("transaction:transaction")


def transactions_list_url(user: User):
    return reverse("transaction:transaction", get={"user": user.external_id})


class TransactionApiTest(TestCase):
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

    def test_create_transaction_by_user_success_payer(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": 10.0,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        transaction = Transaction.objects.get(
            external_id=res.data["external_id"]
        )
        self.assertEqual(transaction.payer, self.user1)
        self.assertEqual(transaction.receiver, self.user2)
        self.assertEqual(transaction.amount, payload["amount"])
        self.assertEqual(transaction.status, 1)
        self.assertIsNone(transaction.declined_comment)
        self.assertEqual(transaction.message, payload["message"])
        self.assertFalse(transaction.is_deleted)

    def test_create_transaction_by_user_success_receiver(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "payer": self.user3.external_id,
            "amount": 10.0,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        transaction = Transaction.objects.get(
            external_id=res.data["external_id"]
        )
        self.assertEqual(transaction.payer, self.user3)
        self.assertEqual(transaction.receiver, self.user1)
        self.assertEqual(transaction.amount, payload["amount"])
        self.assertEqual(transaction.status, 1)
        self.assertIsNone(transaction.declined_comment)
        self.assertEqual(transaction.message, payload["message"])
        self.assertFalse(transaction.is_deleted)

    def test_create_transaction_by_user_fail(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "payer": self.user3.external_id,
            "receiver": self.user2.external_id,
            "amount": 10.0,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_amount_zero(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": 0,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_amount_negative(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": -10,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_no_message(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": 10,
            "message": ""
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_same_user(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user1.external_id,
            "amount": 10.00,
            "message": "first transaction"
        }
        res = self.client.post(TRANSACTION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_list_transaction(self):
        payload1 = {
            "receiver": self.user2.external_id,
            "amount": 10.00,
            "message": "first transaction"
        }
        payload2 = {
            "receiver": self.user3.external_id,
            "amount": 15.00,
            "message": "second transaction"
        }
        payload3 = {
            "receiver": self.user4.external_id,
            "amount": 20.00,
            "message": "third transaction"
        }
        payload4 = {
            "receiver": self.user3.external_id,
            "amount": 25.00,
            "message": "third transaction"
        }

        self.client.force_authenticate(self.user1)
        self.client.post(
            TRANSACTION_URL, payload1, format="json")

        self.client.force_authenticate(self.user2)
        self.client.post(
            TRANSACTION_URL, payload2, format="json")

        self.client.force_authenticate(self.user3)
        transaction3 = self.client.post(
            TRANSACTION_URL, payload3, format="json")

        self.client.force_authenticate(self.user4)
        transaction4 = self.client.post(
            TRANSACTION_URL, payload4, format="json")

        transactions = TransactionSerializer(
            [
                Transaction.objects.get(
                    external_id=transaction3.data["external_id"]),
                Transaction.objects.get(
                    external_id=transaction4.data["external_id"]),
            ],
            many=True
        )
        res = self.client.get(
            f"{TRANSACTION_URL}?user={self.user3.external_id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, transactions.data)

    def test_list_transactions_same_user(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(
            f"{TRANSACTION_URL}?user={self.user1.external_id}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
