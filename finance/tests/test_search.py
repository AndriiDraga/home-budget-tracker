from decimal import Decimal

from django.urls import reverse

from finance.models import Transaction
from .base import BaseFinanceTestCase


class TransactionSearchTest(BaseFinanceTestCase):

    def setUp(self):
        super().setUp()
        Transaction.objects.create(
            amount=Decimal("20.00"), description="Cinema tickets",
            date="2026-08-01", category=self.category_expense, account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("300.00"), description="Rent payment",
            date="2026-08-02", category=self.category_expense, account=self.account,
        )

    def test_search_filters_by_description(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"query": "Cinema"}
        )
        self.assertContains(response, "Cinema tickets")
        self.assertNotContains(response, "Rent payment")

    def test_filter_by_min_amount(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"min_amount": "100"}
        )
        self.assertContains(response, "Rent payment")
        self.assertNotContains(response, "Cinema tickets")


class CategorySearchTest(BaseFinanceTestCase):

    def test_search_filters_by_name(self):
        response = self.client.get(
            reverse("finance:category-list"), {"query": "Groc"}
        )
        self.assertContains(response, "Groceries")
        self.assertNotContains(response, "Salary")
