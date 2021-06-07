from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Transaction, User
from django.urls import reverse
from rest_framework import status

TRANSACTION_CREATE_URL = reverse("transaction:transaction")
# TRANSACTIONS_URL = reverse("transaction:list")


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
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

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
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

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
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_amount_zero(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": 0,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_amount_negative(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": -10,
            "message": "Some transaction"
        }
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_create_transaction_by_user_fail_no_message(self):
        self.client.force_authenticate(self.user1)
        payload = {
            "receiver": self.user2.external_id,
            "amount": 10,
            "message": ""
        }
        res = self.client.post(TRANSACTION_CREATE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    # def test_create_transaction_success(self):
    #     transaction = self.client.post(TRANSACTION_CREATE_URL, {
    #         "payer": self.user1,
    #         "receiver": self.user2,
    #         "amount": 10.00,
    #         "message": "first transaction"
    #     })
    #     res = self.client.get(
    #         reverse('transaction:list', args=(self.user2.id, self.user1.id)))
    #     print(res, res.data)
