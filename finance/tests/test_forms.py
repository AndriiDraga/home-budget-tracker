from finance.forms import TransactionForm
from .base import BaseFinanceTestCase


class TransactionFormValidationTest(BaseFinanceTestCase):

    def test_form_valid_with_correct_data(self):
        form = TransactionForm(
            data={
                "amount": "10.00",
                "description": "Valid",
                "date": "2026-08-01",
                "category": self.category_expense.pk,
                "account": self.account.pk,
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_negative_amount(self):
        form = TransactionForm(
            data={
                "amount": "-10.00",
                "description": "Invalid",
                "date": "2026-08-01",
                "category": self.category_expense.pk,
                "account": self.account.pk,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_form_invalid_with_future_date(self):
        form = TransactionForm(
            data={
                "amount": "10.00",
                "description": "Invalid",
                "date": "2099-01-01",
                "category": self.category_expense.pk,
                "account": self.account.pk,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
