from datetime import timedelta
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import (
    AccountForm,
    CategoryForm,
    OwnerRegistrationForm,
    TransactionForm,
    TransactionSearchForm, CategorySearchForm,
)
from .models import Account, Category, Transaction


@login_required
def index(request: HttpRequest) -> HttpResponse:
    user = request.user

    context: dict[str, int] = {
        "category_count": Category.objects.filter(
            models.Q(owner=user) | models.Q(owner__isnull=True)
        ).count(),
        "account_count": Account.objects.filter(owner=user).count(),
        "transaction_count": Transaction.objects.filter(
            account__owner=user
        ).count(),
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
    paginate_by = 5

    def _get_sort_dirs(self) -> tuple[str | None, str | None]:
        date_dir = self.request.GET.get("date_dir")
        amount_dir = self.request.GET.get("amount_dir")

        if date_dir not in {"asc", "desc"}:
            date_dir = None
        if amount_dir not in {"asc", "desc"}:
            amount_dir = None

        return date_dir, amount_dir

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["search_form"] = TransactionSearchForm(
            self.request.GET, user=self.request.user
        )

        date_dir, amount_dir = self._get_sort_dirs()

        context["current_date_dir"] = date_dir
        context["current_amount_dir"] = amount_dir

        context["date_dir_next"] = "desc" if date_dir == "asc" else "asc"
        context["amount_dir_next"] = "desc" if amount_dir == "asc" else "asc"

        query_params = self.request.GET.copy()
        query_params.pop("date_dir", None)
        query_params.pop("amount_dir", None)
        query_params.pop("page", None)
        context["query_params"] = query_params.urlencode()

        return context

    def get_queryset(self) -> QuerySet[Transaction]:
        queryset = Transaction.objects.filter(
            account__owner=self.request.user
        ).select_related("category", "account")

        form = TransactionSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            category = form.cleaned_data.get("category")
            min_amount = form.cleaned_data.get("min_amount")
            max_amount = form.cleaned_data.get("max_amount")
            period = form.cleaned_data.get("period")

            if query:
                queryset = queryset.filter(description__icontains=query)
            if category:
                queryset = queryset.filter(category=category)
            if min_amount is not None:
                queryset = queryset.filter(amount__gte=min_amount)
            if max_amount is not None:
                queryset = queryset.filter(amount__lte=max_amount)
            if period:
                since = timezone.now().date() - timedelta(days=int(period))
                queryset = queryset.filter(date__gte=since)

        date_dir, amount_dir = self._get_sort_dirs()

        order_fields: list[str] = []

        if date_dir:
            order_fields.append("date" if date_dir == "asc" else "-date")
        if amount_dir:
            order_fields.append("amount" if amount_dir == "asc" else "-amount")

        if not order_fields:
            order_fields = ["-date"]

        queryset = queryset.order_by(*order_fields)

        return queryset

class TransactionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TransactionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.filter(account__owner=self.request.user)


class TransactionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.filter(account__owner=self.request.user)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
    template_name = "finance/category_list.html"
    context_object_name = "category_list"
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = CategorySearchForm(self.request.GET)
        return context

    def get_queryset(self) -> QuerySet[Category]:
        queryset = Category.objects.filter(
            models.Q(owner=self.request.user) | models.Q(owner__isnull=True)
        ).order_by("name")
        form = CategorySearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            category_type = form.cleaned_data.get("category_type")
            if query:
                queryset = queryset.filter(name__icontains=query)
            if category_type:
                queryset = queryset.filter(category_type=category_type)
        return queryset


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category-list")

    def form_valid(self, form: CategoryForm) -> HttpResponse:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category-list")

    def get_queryset(self) -> QuerySet[Category]:
        # редагувати можна тільки свої категорії, не глобальні
        return Category.objects.filter(owner=self.request.user)


class CategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Category
    template_name = "finance/category_confirm_delete.html"
    success_url = reverse_lazy("finance:category-list")

    def get_queryset(self) -> QuerySet[Category]:
        return Category.objects.filter(owner=self.request.user)


class AccountListView(LoginRequiredMixin, generic.ListView):
    model = Account
    template_name = "finance/account_list.html"
    context_object_name = "account_list"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Account]:
        return Account.objects.filter(owner=self.request.user).order_by("name")


class AccountCreateView(LoginRequiredMixin, generic.CreateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account-list")

    def form_valid(self, form: AccountForm) -> HttpResponse:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account-list")

    def get_queryset(self) -> QuerySet[Account]:
        return Account.objects.filter(owner=self.request.user)


class AccountDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Account
    template_name = "finance/account_confirm_delete.html"
    success_url = reverse_lazy("finance:account-list")

    def get_queryset(self) -> QuerySet[Account]:
        return Account.objects.filter(owner=self.request.user)