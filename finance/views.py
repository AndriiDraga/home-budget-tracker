from datetime import timedelta
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models.functions import TruncWeek
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.db.models import Sum


from finance.forms import (
    AccountForm,
    AccountInvitationForm,
    CategoryForm,
    OwnerRegistrationForm,
    TransactionForm,
    TransactionSearchForm, CategorySearchForm,
)
from finance.models import (
    Account,
    AccountInvitation,
    AccountMembership,
    Category,
    Owner,
    Transaction,
)


GENERIC_INVITATION_RESPONSE = (
    "If a matching user exists and can be invited, the invitation has been created."
)


def accounts_for_user(user: Owner) -> QuerySet[Account]:
    return Account.objects.filter(memberships__user=user).distinct()


def owner_accounts_for_user(user: Owner) -> QuerySet[Account]:
    return Account.objects.filter(
        memberships__user=user,
        memberships__role=AccountMembership.Role.OWNER,
    ).distinct()


def transactions_for_user(user: Owner) -> QuerySet[Transaction]:
    return Transaction.objects.filter(account__memberships__user=user).distinct()


@login_required
def index(request: HttpRequest) -> HttpResponse:
    user = request.user

    context: dict[str, int] = {
        "category_count": Category.objects.filter(
            models.Q(owner=user) | models.Q(owner__isnull=True)
        ).count(),
        "account_count": accounts_for_user(user).count(),
        "transaction_count": transactions_for_user(user).count(),
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
        queryset = transactions_for_user(self.request.user).select_related(
            "category", "account"
        )

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

    def form_valid(self, form: TransactionForm) -> HttpResponse:
        form.instance.created_by = self.request.user
        return super().form_valid(form)


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
        return transactions_for_user(self.request.user)


class TransactionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("finance:transaction-list")

    def get_queryset(self) -> QuerySet[Transaction]:
        return transactions_for_user(self.request.user)


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
        return accounts_for_user(self.request.user).order_by("name")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["owner_account_ids"] = set(
            owner_accounts_for_user(self.request.user).values_list("pk", flat=True)
        )
        return context


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
        return owner_accounts_for_user(self.request.user)


class AccountDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Account
    template_name = "finance/account_confirm_delete.html"
    success_url = reverse_lazy("finance:account-list")

    def get_queryset(self) -> QuerySet[Account]:
        return owner_accounts_for_user(self.request.user)


class AccountDetailView(LoginRequiredMixin, generic.DetailView):
    model = Account
    template_name = "finance/account_detail.html"
    context_object_name = "account"

    def get_queryset(self) -> QuerySet[Account]:
        return accounts_for_user(self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["is_account_owner"] = AccountMembership.objects.filter(
            account=self.object,
            user=self.request.user,
            role=AccountMembership.Role.OWNER,
        ).exists()
        return context


class AccountInviteView(LoginRequiredMixin, generic.FormView):
    form_class = AccountInvitationForm
    template_name = "finance/account_invite.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.account = get_object_or_404(
            owner_accounts_for_user(request.user),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["account"] = self.account
        return context

    def form_valid(self, form: AccountInvitationForm) -> HttpResponse:
        value = form.cleaned_data["username_or_email"].strip()
        invited_user = Owner.objects.filter(
            models.Q(username=value) | models.Q(email=value)
        ).first()

        if invited_user and invited_user != self.request.user:
            is_member = AccountMembership.objects.filter(
                account=self.account,
                user=invited_user,
            ).exists()
            has_pending_invitation = AccountInvitation.objects.filter(
                account=self.account,
                invited_user=invited_user,
                status=AccountInvitation.Status.PENDING,
            ).exists()
            if not is_member and not has_pending_invitation:
                AccountInvitation.objects.create(
                    account=self.account,
                    invited_user=invited_user,
                    invited_by=self.request.user,
                )

        messages.info(self.request, GENERIC_INVITATION_RESPONSE)
        return redirect("finance:account-detail", pk=self.account.pk)


class AccountMembersView(LoginRequiredMixin, generic.ListView):
    model = AccountMembership
    template_name = "finance/account_members.html"
    context_object_name = "memberships"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.account = get_object_or_404(
            owner_accounts_for_user(request.user),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[AccountMembership]:
        return AccountMembership.objects.filter(account=self.account).select_related("user")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["account"] = self.account
        return context


class AccountMemberRemoveView(LoginRequiredMixin, generic.View):
    def post(self, request: HttpRequest, account_pk: int, membership_pk: int) -> HttpResponse:
        account = get_object_or_404(owner_accounts_for_user(request.user), pk=account_pk)
        membership = get_object_or_404(
            AccountMembership,
            pk=membership_pk,
            account=account,
        )
        if membership.role != AccountMembership.Role.OWNER:
            membership.delete()
        return redirect("finance:account-members", pk=account.pk)


class InvitationListView(LoginRequiredMixin, generic.ListView):
    model = AccountInvitation
    template_name = "finance/invitation_list.html"
    context_object_name = "invitations"

    def get_queryset(self) -> QuerySet[AccountInvitation]:
        return AccountInvitation.objects.filter(
            invited_user=self.request.user,
            status=AccountInvitation.Status.PENDING,
        ).select_related("account", "invited_by")


class InvitationAcceptView(LoginRequiredMixin, generic.View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        invitation = get_object_or_404(
            AccountInvitation,
            pk=pk,
            invited_user=request.user,
            status=AccountInvitation.Status.PENDING,
        )
        with db_transaction.atomic():
            AccountMembership.objects.get_or_create(
                account=invitation.account,
                user=request.user,
                defaults={"role": AccountMembership.Role.MEMBER},
            )
            invitation.status = AccountInvitation.Status.ACCEPTED
            invitation.save(update_fields=["status", "updated_at"])
        return redirect("finance:invitation-list")


class InvitationRejectView(LoginRequiredMixin, generic.View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        invitation = get_object_or_404(
            AccountInvitation,
            pk=pk,
            invited_user=request.user,
            status=AccountInvitation.Status.PENDING,
        )
        invitation.status = AccountInvitation.Status.REJECTED
        invitation.save(update_fields=["status", "updated_at"])
        return redirect("finance:invitation-list")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finance/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        transactions = transactions_for_user(user)

        total_expense = (
                transactions.filter(
                    category__category_type="expense").aggregate(total=Sum("amount")
                                                                 )["total"]
                or 0
        )
        total_income = (
                transactions.filter(
                    category__category_type="income").aggregate(total=Sum("amount")
                                                                )["total"]
                or 0
        )
        total_balance = (
                accounts_for_user(user).aggregate(total=Sum("balance"))["total"] or 0
        )

        # Розбивка витрат по категоріях (для donut-чарту витрат)
        expense_breakdown = list(
            transactions.filter(category__category_type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        # Розбивка доходів по категоріях (для donut-чарту доходів)
        income_breakdown = list(
            transactions.filter(category__category_type="income")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        # Тренд доходів/витрат по тижнях за останні 12 тижнів (для лінійного графіка)
        weeks_back = 12
        period_start = timezone.now().date() - timedelta(weeks=weeks_back)
        weekly = (
            transactions.filter(date__gte=period_start)
            .annotate(week=TruncWeek("date"))
            .values("week", "category__category_type")
            .annotate(total=Sum("amount"))
            .order_by("week")
        )

        # Повний ряд тижнів, включно з тими, де не було жодної транзакції (нуль)
        first_monday = period_start - timedelta(days=period_start.weekday())
        today_monday = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        weeks = []
        current = first_monday
        while current <= today_monday:
            weeks.append(current)
            current += timedelta(weeks=1)

        expense_by_week = {w: 0.0 for w in weeks}
        income_by_week = {w: 0.0 for w in weeks}
        for row in weekly:
            week_key = row["week"]
            if week_key not in expense_by_week:
                continue
            if row["category__category_type"] == "expense":
                expense_by_week[week_key] = float(row["total"])
            elif row["category__category_type"] == "income":
                income_by_week[week_key] = float(row["total"])

        context.update(
            {
                "total_expense": total_expense,
                "total_income": total_income,
                "total_balance": total_balance,
                "transaction_count": transactions.count(),
                "expense_category_labels": [row["category__name"] for row in expense_breakdown],
                "expense_category_totals": [float(row["total"]) for row in expense_breakdown],
                "income_category_labels": [row["category__name"] for row in income_breakdown],
                "income_category_totals": [float(row["total"]) for row in income_breakdown],
                "trend_labels": [w.strftime("%d %b") for w in weeks],
                "trend_expense": [expense_by_week[w] for w in weeks],
                "trend_income": [income_by_week[w] for w in weeks],
                "recent_transactions": transactions.select_related("category", "account").order_by(
                    "-date"
                )[:8],
            }
        )
        return context
