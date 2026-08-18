from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Owner, Transaction, Category, Account
from django.db import models


class OwnerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Owner
        fields = UserCreationForm.Meta.fields


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "description", "date", "category", "account"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # показуємо лише рахунки цього юзера
            self.fields["account"].queryset = Account.objects.filter(owner=user)
            # показуємо глобальні категорії + власні юзера
            self.fields["category"].queryset = Category.objects.filter(
                models.Q(owner=user) | models.Q(owner__isnull=True)
            )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "category_type"]
        

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "account_type", "balance"]
