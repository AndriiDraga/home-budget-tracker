from django.db.models import F
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from finance.models import Transaction, Account


def _get_effect(amount, category_type):
    return amount if category_type == "income" else -amount


@receiver(pre_save, sender=Transaction)
def rollback_old_transaction_effect(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = Transaction.objects.select_related("category").get(pk=instance.pk)
    except Transaction.DoesNotExist:
        return

    old_effect = _get_effect(old_instance.amount, old_instance.category.category_type)

    Account.objects.filter(pk=old_instance.account_id).update(
        balance=F("balance") - old_effect
    )


@receiver(post_save, sender=Transaction)
def apply_new_transaction_effect(sender, instance, created, **kwargs):
    new_effect = _get_effect(instance.amount, instance.category.category_type)

    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") + new_effect
    )


@receiver(post_delete, sender=Transaction)
def rollback_deleted_transaction_effect(sender, instance, **kwargs):
    effect = _get_effect(instance.amount, instance.category.category_type)

    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") - effect
    )
