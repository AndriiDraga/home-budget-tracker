from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("", views.index, name="index"),

    path("register/", views.RegisterView.as_view(), name="register"),

    path(
        "transactions/",
        views.TransactionListView.as_view(),
        name="transaction-list",
    ),
    path(
        "transactions/create/",
        views.TransactionCreateView.as_view(),
        name="transaction-create",
    ),
    path(
        "transactions/<int:pk>/update/",
        views.TransactionUpdateView.as_view(),
        name="transaction-update",
    ),
    path(
        "transactions/<int:pk>/delete/",
        views.TransactionDeleteView.as_view(),
        name="transaction-delete",
    ),

    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/update/", views.CategoryUpdateView.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),

    path("accounts/", views.AccountListView.as_view(), name="account-list"),
    path("accounts/create/", views.AccountCreateView.as_view(), name="account-create"),
    path("accounts/<int:pk>/update/", views.AccountUpdateView.as_view(), name="account-update"),
    path("accounts/<int:pk>/delete/", views.AccountDeleteView.as_view(), name="account-delete"),
]
