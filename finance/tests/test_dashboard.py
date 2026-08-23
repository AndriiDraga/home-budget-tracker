from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from finance.models import Transaction
from finance.tests.base import BaseFinanceTestCase


class DashboardViewTest(BaseFinanceTestCase):

    def test_dashboard_redirects_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse("finance:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_returns_200_for_logged_in_user(self):
        response = self.client.get(reverse("finance:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_totals_with_no_transactions(self):
        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(response.context["total_expense"], 0)
        self.assertEqual(response.context["total_income"], 0)
        self.assertEqual(response.context["transaction_count"], 0)
        self.assertEqual(response.context["total_balance"], Decimal("500.00"))
        self.assertEqual(response.context["expense_category_labels"], [])
        self.assertEqual(response.context["income_category_labels"], [])
        self.assertEqual(list(response.context["recent_transactions"]), [])

    def test_dashboard_calculates_income_and_expense_totals(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Groceries run",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("50.00"),
            description="More groceries",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("1000.00"),
            description="Paycheck",
            date=timezone.now().date(),
            category=self.category_income,
            account=self.account,
        )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(response.context["total_expense"], Decimal("150.00"))
        self.assertEqual(response.context["total_income"], Decimal("1000.00"))
        self.assertEqual(response.context["transaction_count"], 3)

    def test_dashboard_expense_category_breakdown(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Groceries run",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.account,
        )
        Transaction.objects.create(
            amount=Decimal("50.00"),
            description="More groceries",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.account,
        )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(
            response.context["expense_category_labels"], ["Groceries"]
        )
        self.assertEqual(
            response.context["expense_category_totals"], [150.0]
        )

    def test_dashboard_income_category_breakdown(self):
        Transaction.objects.create(
            amount=Decimal("1000.00"),
            description="Paycheck",
            date=timezone.now().date(),
            category=self.category_income,
            account=self.account,
        )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(
            response.context["income_category_labels"], ["Salary"]
        )
        self.assertEqual(
            response.context["income_category_totals"], [1000.0]
        )

    def test_dashboard_trend_excludes_transactions_older_than_12_weeks(self):
        old_date = timezone.now().date() - timedelta(weeks=20)
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Old expense",
            date=old_date,
            category=self.category_expense,
            account=self.account,
        )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(sum(response.context["trend_expense"]), 0.0)
        self.assertEqual(sum(response.context["trend_income"]), 0.0)

    def test_dashboard_recent_transactions_limited_to_eight(self):
        for i in range(10):
            Transaction.objects.create(
                amount=Decimal("10.00"),
                description=f"Expense {i}",
                date=timezone.now().date() - timedelta(days=i),
                category=self.category_expense,
                account=self.account,
            )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(len(response.context["recent_transactions"]), 8)

    def test_dashboard_isolates_other_users_data(self):
        other_user = self.user.__class__.objects.create_user(
            username="other.owner", password="password123"
        )
        other_account = self.account.__class__.objects.create(
            name="Other account",
            account_type="cash",
            balance=Decimal("300.00"),
            owner=other_user,
        )
        Transaction.objects.create(
            amount=Decimal("999.00"),
            description="Not mine",
            date=timezone.now().date(),
            category=self.category_expense,
            account=other_account,
        )

        response = self.client.get(reverse("finance:dashboard"))

        self.assertEqual(response.context["total_expense"], 0)
        self.assertEqual(response.context["transaction_count"], 0)
        self.assertEqual(response.context["total_balance"], Decimal("500.00"))
