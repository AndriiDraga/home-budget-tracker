from decimal import Decimal

from django.urls import reverse

from finance.models import Transaction
from .base import BaseFinanceTestCase


class TransactionSortingTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()
        Transaction.objects.create(
            amount=Decimal("50.00"), description="A",
            date="2026-08-01", category=self.category_expense, account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("10.00"), description="B",
            date="2026-08-01", category=self.category_expense, account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("30.00"), description="C",
            date="2026-08-02", category=self.category_expense, account=self.account,
        )

    def test_sort_by_amount_only(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"amount_dir": "asc"}
        )
        descriptions = [t.description for t in response.context["transaction_list"]]
        self.assertEqual(descriptions, ["B", "C", "A"])

    def test_sort_by_date_priority_with_amount_tiebreaker(self):
        response = self.client.get(
            reverse("finance:transaction-list"),
            {"date_dir": "asc", "amount_dir": "asc"},
        )
        descriptions = [t.description for t in response.context["transaction_list"]]
        self.assertEqual(descriptions, ["B", "A", "C"])
