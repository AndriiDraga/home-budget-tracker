from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from finance.models import Account, Category, Owner, Transaction


class Command(BaseCommand):
    help = "Load sample accounts and transactions for the admin user"

    def handle(self, *args, **options):
        try:
            admin = Owner.objects.get(username="admin")
        except Owner.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'admin' not found. Create a superuser first."))
            return

        account, created = Account.objects.get_or_create(
            name="Main card",
            owner=admin,
            defaults={"account_type": "card", "balance": 1500},
        )
        self.stdout.write(self.style.SUCCESS(f"Account: {account.name} ({'created' if created else 'exists'})"))

        savings, created = Account.objects.get_or_create(
            name="Savings",
            owner=admin,
            defaults={"account_type": "savings", "balance": 3000},
        )
        self.stdout.write(self.style.SUCCESS(f"Account: {savings.name} ({'created' if created else 'exists'})"))

        today = timezone.now().date()

        sample_transactions = [
            (150.50, "Groceries", "Groceries", account, 2),
            (45.00, "Metro card top-up", "Transport", account, 5),
            (2000.00, "Monthly salary", "Salary", account, 8),
            (89.99, "Electricity bill", "Utilities", account, 12),
            (25.00, "Cinema", "Entertainment", account, 18),
            (600.00, "Rent payment", "Rent", account, 25),
            (120.00, "Doctor visit", "Health", savings, 35),
            (300.00, "Freelance project", "Freelance", savings, 45),
        ]

        created_count = 0
        for amount, description, category_name, target_account, days_ago in sample_transactions:
            try:
                category = Category.objects.get(name=category_name, owner__isnull=True)
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Category '{category_name}' not found, skipping."))
                continue

            _, created = Transaction.objects.get_or_create(
                amount=amount,
                description=description,
                date=today - timedelta(days=days_ago),
                category=category,
                account=target_account,
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} sample transactions."))
