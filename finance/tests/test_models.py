from decimal import Decimal

from finance.models import Transaction
from finance.tests.base import BaseFinanceTestCase


class ModelTest(BaseFinanceTestCase):

    def test_category_str(self):
        self.assertEqual(str(self.category_expense), "Groceries")

    def test_account_str(self):
        self.assertEqual(str(self.account), "Main card")

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            amount=Decimal("50.00"),
            description="Food",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.assertEqual(str(transaction), "50.00 - Food")
