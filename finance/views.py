from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import OwnerRegistrationForm, TransactionForm, CategoryForm, AccountForm
from .models import Category, Account, Transaction
from django.db import models


@login_required
def index(request):
    context = {
        "category_count": Category.objects.count(),
        "account_count": Account.objects.count(),
        "transaction_count": Transaction.objects.count(),
    }
    return render(request, "finance/index.html", context)


class RegisterView(generic.CreateView):
    form_class = OwnerRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class TransactionListView(LoginRequiredMixin, generic.ListView):
    model = Transaction
    template_name = "finance/transaction_list.html"
    context_object_name = "transaction_list"
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(
            account__owner=self.request.user
        ).select_related("category", "account")


class TransactionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TransactionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Transaction.objects.filter(account__owner=self.request.user)


class TransactionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_queryset(self):
        return Transaction.objects.filter(account__owner=self.request.user)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
    template_name = "finance/category_list.html"
    context_object_name = "category_list"
    paginate_by = 10

    def get_queryset(self):
        # свої категорії + глобальні (owner=None)
        return Category.objects.filter(
            models.Q(owner=self.request.user) | models.Q(owner__isnull=True)
        )


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category-list")

    def get_queryset(self):
        # редагувати можна тільки свої категорії, не глобальні
        return Category.objects.filter(owner=self.request.user)


class CategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Category
    template_name = "finance/category_confirm_delete.html"
    success_url = reverse_lazy("finance:category-list")

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

# finance/views.py
class AccountListView(LoginRequiredMixin, generic.ListView):
    model = Account
    template_name = "finance/account_list.html"
    context_object_name = "account_list"
    paginate_by = 10

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)


class AccountCreateView(LoginRequiredMixin, generic.CreateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account-list")

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)


class AccountDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Account
    template_name = "finance/account_confirm_delete.html"
    success_url = reverse_lazy("finance:account-list")

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)
