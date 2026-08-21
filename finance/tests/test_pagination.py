from decimal import Decimal
from django.db import models

from django.urls import reverse

from finance.models import Transaction, Category, Account
from .base import BaseFinanceTestCase


class TransactionPaginationTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()
        for i in range(15):
            Transaction.objects.create(
                amount=Decimal("10.00"),
                description=f"Transaction {i}",
                date="2026-08-01",
                category=self.category_expense,
                account=self.account,
            )

    def test_first_page_has_ten_items(self):
        response = self.client.get(reverse("finance:transaction-list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["transaction_list"]), 5)

    def test_second_page_has_remaining_items(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"page": 2}
        )
        self.assertEqual(len(response.context["transaction_list"]), 5)


class CategoryPaginationTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()
        for i in range(12):
            Category.objects.create(
                name=f"Category {i}", category_type="expense", owner=self.user
            )
        self.total_categories = Category.objects.filter(
            models.Q(owner=self.user) | models.Q(owner__isnull=True)
        ).count()

    def test_first_page_has_ten_items(self):
        response = self.client.get(reverse("finance:category-list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["category_list"]), 10)

    def test_second_page_has_remaining_items(self):
        response = self.client.get(reverse("finance:category-list"), {"page": 2})
        expected_on_second_page = min(10, self.total_categories - 10)
        self.assertEqual(len(response.context["category_list"]), expected_on_second_page)


class AccountPaginationTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()
        for i in range(12):
            Account.objects.create(
                name=f"Account {i}",
                account_type="card",
                balance=Decimal("0.00"),
                owner=self.user,
            )

    def test_first_page_has_ten_items(self):
        response = self.client.get(reverse("finance:account-list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["account_list"]), 10)

    def test_second_page_has_remaining_items(self):
        response = self.client.get(reverse("finance:account-list"), {"page": 2})
        self.assertEqual(len(response.context["account_list"]), 3)
