from decimal import Decimal

from finance.models import Transaction, Category, Account
from .base import BaseFinanceTestCase


class TransactionCRUDTest(BaseFinanceTestCase):

    def test_create_transaction(self):
        response = self.client.post(
            "/transactions/create/",
            data={
                "amount": "45.00",
                "description": "New purchase",
                "date": "2026-08-01",
                "category": self.category_expense.pk,
                "account": self.account.pk,
            },
        )
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_update_transaction(self):
        transaction = Transaction.objects.create(
            amount=Decimal("50.00"),
            description="Old description",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.client.post(
            f"/transactions/{transaction.pk}/update/",
            data={
                "amount": "60.00",
                "description": "Updated description",
                "date": "2026-08-01",
                "category": self.category_expense.pk,
                "account": self.account.pk,
            },
        )
        transaction.refresh_from_db()
        self.assertEqual(transaction.description, "Updated description")
        self.assertEqual(transaction.amount, Decimal("60.00"))

    def test_delete_transaction(self):
        transaction = Transaction.objects.create(
            amount=Decimal("50.00"),
            description="To be deleted",
            date="2026-08-01",
            category=self.category_expense,
            account=self.account,
        )
        self.client.post(f"/transactions/{transaction.pk}/delete/")
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())


class CategoryCRUDTest(BaseFinanceTestCase):

    def test_create_category(self):
        response = self.client.post(
            "/categories/create/",
            data={"name": "Entertainment", "category_type": "expense"},
        )
        self.assertTrue(
            Category.objects.filter(name="Entertainment", owner=self.user).exists()
        )
        self.assertEqual(response.status_code, 302)

    def test_update_own_category(self):
        category = Category.objects.create(
            name="Old name", category_type="expense", owner=self.user
        )
        self.client.post(
            f"/categories/{category.pk}/update/",
            data={"name": "New name", "category_type": "expense"},
        )
        category.refresh_from_db()
        self.assertEqual(category.name, "New name")

    def test_delete_own_category(self):
        category = Category.objects.create(
            name="To delete", category_type="expense", owner=self.user
        )
        self.client.post(f"/categories/{category.pk}/delete/")
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())


class AccountCRUDTest(BaseFinanceTestCase):

    def test_create_account(self):
        response = self.client.post(
            "/accounts/create/",
            data={
                "name": "New savings",
                "account_type": "savings",
                "balance": "0.00",
            },
        )
        self.assertTrue(
            Account.objects.filter(name="New savings", owner=self.user).exists()
        )
        self.assertEqual(response.status_code, 302)

    def test_update_own_account(self):
        self.client.post(
            f"/accounts/{self.account.pk}/update/",
            data={
                "name": "Renamed card",
                "account_type": "card",
                "balance": str(self.account.balance),
            },
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, "Renamed card")

    def test_delete_own_account(self):
        self.client.post(f"/accounts/{self.account.pk}/delete/")
        self.assertFalse(Account.objects.filter(pk=self.account.pk).exists())
