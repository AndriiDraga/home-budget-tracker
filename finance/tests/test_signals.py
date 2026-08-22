from decimal import Decimal

from finance.models import Account, Transaction
from finance.tests.base import BaseFinanceTestCase


class AccountBalanceSignalTest(BaseFinanceTestCase):

    def test_balance_increases_on_income_transaction_create(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Freelance",
            date="2026-08-01",
            category=self.category_income,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("600.00"))

    def test_balance_decreases_on_expense_transaction_create(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Food",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("400.00"))

    def test_balance_updates_correctly_when_amount_changed(self):
        transaction = Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Food",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("400.00"))

        transaction.amount = Decimal("150.00")
        transaction.save()

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("350.00"))

    def test_balance_updates_when_category_type_changed(self):
        transaction = Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Something",
            date="2026-08-01",
            category=self.category_income,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("600.00"))

        transaction.category = self.category_expense
        transaction.save()

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("400.00"))

    def test_balance_updates_when_transaction_moved_to_another_account(self):
        second_account = Account.objects.create(
            name="Savings",
            account_type="savings",
            balance=Decimal("200.00"),
            owner=self.user,
        )
        transaction = Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Food",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("400.00"))

        transaction.account = second_account
        transaction.save()

        self.account.refresh_from_db()
        second_account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("500.00"))
        self.assertEqual(second_account.balance, Decimal("100.00"))

    def test_balance_restores_on_transaction_delete(self):
        transaction = Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Food",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("400.00"))

        transaction.delete()

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("500.00"))
