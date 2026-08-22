from datetime import date
from decimal import Decimal
from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.utils import timezone

from finance.models import Account, Category, Owner, Transaction


class OwnerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Owner
        fields = UserCreationForm.Meta.fields


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ["amount", "description", "date", "category", "account"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(
        self,
        *args: Any,
        user: Owner | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if user:
            self.fields["account"].queryset = Account.objects.filter(owner=user)
            self.fields["category"].queryset = Category.objects.filter(
                models.Q(owner=user) | models.Q(owner__isnull=True)
            )

    def clean_amount(self) -> Decimal | None:
        amount: Decimal | None = self.cleaned_data.get("amount")

        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        return amount

    def clean_date(self) -> date | None:
        transaction_date: date | None = self.cleaned_data.get("date")

        if transaction_date and transaction_date > timezone.now().date():
            raise forms.ValidationError("Transaction date cannot be in the future.")

        return transaction_date


PERIOD_CHOICES = [
    ("", "All time"),
    ("7", "Last 7 days"),
    ("14", "Last 14 days"),
    ("30", "Last 30 days"),
]


class TransactionSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by description..."}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="",
        empty_label="All categories",
    )
    min_amount = forms.DecimalField(
        required=False,
        label="",
        widget=forms.NumberInput(attrs={"placeholder": "Min amount"}),
    )
    max_amount = forms.DecimalField(
        required=False,
        label="",
        widget=forms.NumberInput(attrs={"placeholder": "Max amount"}),
    )
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=False,
        label="",
    )

    def __init__(
        self,
        *args: Any,
        user: Owner | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = Category.objects.filter(
                models.Q(owner=user) | models.Q(owner__isnull=True)
            )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "category_type"]


class CategorySearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name..."}),
    )
    category_type = forms.ChoiceField(
        choices=[("", "All types"), ("income", "Income"), ("expense", "Expense")],
        required=False,
        label="",
    )


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "account_type", "balance"]
