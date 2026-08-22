from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from finance.models import Owner, Category, Account, Transaction

admin.site.register(Owner, UserAdmin)
admin.site.register(Category)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "balance", "account_type")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "category", "account")
    list_filter = ("category",)
