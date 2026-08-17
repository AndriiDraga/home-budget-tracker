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


    def __str__(self):
        return f"{self.amount} - {self.description}"
