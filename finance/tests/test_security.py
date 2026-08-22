from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from finance.models import Owner, Account, Transaction
from finance.tests.base import BaseFinanceTestCase


class DataIsolationTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()

        self.other_user = Owner.objects.create_user(
            username="other.owner", password="password123"
        )
        self.other_account = Account.objects.create(
            name="Other's card",
            account_type="card",
            balance=Decimal("300.00"),
            owner=self.other_user,
        )
        self.other_transaction = Transaction.objects.create(
            amount=Decimal("77.00"),
            description="Secret purchase",
            date="2026-08-01",
            category=self.category_expense,
            account=self.other_account,
        )

    def test_user_does_not_see_other_users_transactions(self):
        response = self.client.get(reverse("finance:transaction-list"))
        self.assertNotContains(response, "Secret purchase")

    def test_user_does_not_see_other_users_accounts(self):
        response = self.client.get(reverse("finance:account-list"))
        self.assertNotContains(response, "Other's card")

    def test_index_counters_do_not_include_other_users_data(self):
        response = self.client.get(reverse("finance:index"))
        self.assertEqual(response.context["account_count"], 1)
        self.assertEqual(response.context["transaction_count"], 0)

    def test_user_cannot_update_other_users_transaction(self):
        response = self.client.get(
            reverse("finance:transaction-update", args=[self.other_transaction.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_users_transaction(self):
        response = self.client.post(
            reverse("finance:transaction-delete", args=[self.other_transaction.pk])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Transaction.objects.filter(pk=self.other_transaction.pk).exists()
        )


class AccessControlTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_transaction_list_redirects_anonymous_user(self):
        response = self.client.get(reverse("finance:transaction-list"))
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('finance:transaction-list')}"
        )

    def test_account_list_redirects_anonymous_user(self):
        response = self.client.get(reverse("finance:account-list"))
        self.assertEqual(response.status_code, 302)

    def test_category_list_redirects_anonymous_user(self):
        response = self.client.get(reverse("finance:category-list"))
        self.assertEqual(response.status_code, 302)

    def test_index_redirects_anonymous_user(self):
        response = self.client.get(reverse("finance:index"))
        self.assertEqual(response.status_code, 302)
