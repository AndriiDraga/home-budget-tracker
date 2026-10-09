from django.db import models
from django.contrib.auth.models import AbstractUser


class Owner(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=63)
    category_type = models.CharField(max_length=63)
    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=63)
    account_type = models.CharField(max_length=63)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class AccountMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MEMBER = "member", "Member"

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name="account_memberships",
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "user"],
                name="unique_account_membership",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.account} ({self.role})"


class AccountInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invited_user = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name="account_invitations",
    )
    invited_by = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name="sent_account_invitations",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invited_user} -> {self.account} ({self.status})"


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.CharField(max_length=63)
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    created_by = models.ForeignKey(
        Owner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_transactions",
    )

    def __str__(self):
        return f"{self.amount} - {self.description}"
