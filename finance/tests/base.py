from decimal import Decimal

from django.test import TestCase, Client

from finance.models import Owner, Category, Account


class BaseFinanceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "test.owner"
        self.password = "password123"
        self.user = Owner.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.force_login(self.user)

        self.category_expense = Category.objects.create(
            name="Groceries", category_type="expense", owner=None
        )
        self.category_income = Category.objects.create(
            name="Salary", category_type="income", owner=None
        )
        self.account = Account.objects.create(
            name="Main card",
            account_type="card",
            balance=Decimal("500.00"),
            owner=self.user,
        )
