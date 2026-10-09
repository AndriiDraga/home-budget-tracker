from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from finance.models import (
    Account,
    AccountInvitation,
    AccountMembership,
    Category,
    Owner,
    Transaction,
)

admin.site.register(Owner, UserAdmin)
admin.site.register(Category)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "balance", "account_type")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "category", "account", "created_by")
    list_filter = ("category",)


@admin.register(AccountMembership)
class AccountMembershipAdmin(admin.ModelAdmin):
    list_display = ("account", "user", "role")
    list_filter = ("role",)


@admin.register(AccountInvitation)
class AccountInvitationAdmin(admin.ModelAdmin):
    list_display = ("account", "invited_user", "invited_by", "status", "created_at")
    list_filter = ("status",)
