from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

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
        Transaction.objects.create(
            amount=Decimal("1000.00"), description="Monthly salary",
            date="2026-08-03", category=self.category_income, account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("15.00"), description="Today coffee",
            date=timezone.now().date(), category=self.category_expense, account=self.account,
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

    def test_filter_by_max_amount(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"max_amount": "50"}
        )
        self.assertContains(response, "Cinema tickets")
        self.assertNotContains(response, "Rent payment")

    def test_filter_by_category(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"category": self.category_income.pk}
        )
        self.assertContains(response, "Monthly salary")
        self.assertNotContains(response, "Cinema tickets")
        self.assertNotContains(response, "Rent payment")

    def test_filter_by_period(self):
        response = self.client.get(
            reverse("finance:transaction-list"), {"period": "7"}
        )
        self.assertContains(response, "Today coffee")
        self.assertNotContains(response, "Cinema tickets")
        self.assertNotContains(response, "Rent payment")


class CategorySearchTest(BaseFinanceTestCase):

    def test_search_filters_by_name(self):
        response = self.client.get(
            reverse("finance:category-list"), {"query": "Groc"}
        )
        self.assertContains(response, "Groceries")
        self.assertNotContains(response, "Salary")

    def test_filter_by_category_type(self):
        response = self.client.get(
            reverse("finance:category-list"), {"category_type": "income"}
        )
        self.assertContains(response, "Salary")
        self.assertNotContains(response, "Groceries")
