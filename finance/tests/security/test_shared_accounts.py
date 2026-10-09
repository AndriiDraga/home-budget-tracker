from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from finance.models import (
    Account,
    AccountInvitation,
    AccountMembership,
    Owner,
    Transaction,
)
from finance.tests.base import BaseFinanceTestCase


class SharedAccountSecurityTest(BaseFinanceTestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.user
        self.member = Owner.objects.create_user(
            username="family.member",
            email="member@example.com",
            password="password123",
        )
        self.outsider = Owner.objects.create_user(
            username="outside.user",
            email="outsider@example.com",
            password="password123",
        )
        self.shared_account = Account.objects.create(
            name="Shared wallet",
            account_type="cash",
            balance=Decimal("1000.00"),
            owner=self.owner,
        )
        AccountMembership.objects.get_or_create(
            account=self.shared_account,
            user=self.owner,
            defaults={"role": AccountMembership.Role.OWNER},
        )
        self.owner_membership = AccountMembership.objects.get(
            account=self.shared_account,
            user=self.owner,
        )
        self.member_membership = AccountMembership.objects.create(
            account=self.shared_account,
            user=self.member,
            role=AccountMembership.Role.MEMBER,
        )

    def login(self, user):
        self.client.force_login(user)

    def invite_url(self):
        return reverse("finance:account-invite", args=[self.shared_account.pk])

    def members_url(self):
        return reverse("finance:account-members", args=[self.shared_account.pk])

    def remove_member_url(self, membership):
        return reverse(
            "finance:account-member-remove",
            args=[self.shared_account.pk, membership.pk],
        )

    def invitation_accept_url(self, invitation):
        return reverse("finance:invitation-accept", args=[invitation.pk])

    def invitation_reject_url(self, invitation):
        return reverse("finance:invitation-reject", args=[invitation.pk])

    def create_pending_invitation(self, invited_user=None):
        return AccountInvitation.objects.create(
            account=self.shared_account,
            invited_user=invited_user or self.outsider,
            invited_by=self.owner,
            status=AccountInvitation.Status.PENDING,
        )

    def test_owner_sees_own_account(self):
        self.login(self.owner)
        response = self.client.get(reverse("finance:account-list"))
        self.assertContains(response, "Shared wallet")

    def test_member_sees_shared_account(self):
        self.login(self.member)
        response = self.client.get(reverse("finance:account-list"))
        self.assertContains(response, "Shared wallet")

    def test_outsider_does_not_see_shared_account(self):
        self.login(self.outsider)
        response = self.client.get(reverse("finance:account-list"))
        self.assertNotContains(response, "Shared wallet")

    def test_outsider_direct_account_access_returns_403_or_404(self):
        self.login(self.outsider)
        response = self.client.get(
            reverse("finance:account-detail", args=[self.shared_account.pk])
        )
        self.assertIn(response.status_code, [403, 404])

    def test_outsider_cannot_update_shared_account(self):
        self.login(self.outsider)
        response = self.client.post(
            reverse("finance:account-update", args=[self.shared_account.pk]),
            data={"name": "Stolen", "account_type": "cash", "balance": "1.00"},
        )
        self.assertEqual(response.status_code, 404)
        self.shared_account.refresh_from_db()
        self.assertEqual(self.shared_account.name, "Shared wallet")

    def test_outsider_cannot_delete_shared_account(self):
        self.login(self.outsider)
        response = self.client.post(
            reverse("finance:account-delete", args=[self.shared_account.pk])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Account.objects.filter(pk=self.shared_account.pk).exists())

    def test_member_cannot_edit_account_itself(self):
        self.login(self.member)
        response = self.client.post(
            reverse("finance:account-update", args=[self.shared_account.pk]),
            data={"name": "Member edit", "account_type": "cash", "balance": "1.00"},
        )
        self.assertEqual(response.status_code, 404)

    def test_member_cannot_delete_account_itself(self):
        self.login(self.member)
        response = self.client.post(
            reverse("finance:account-delete", args=[self.shared_account.pk])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Account.objects.filter(pk=self.shared_account.pk).exists())

    def test_owner_can_create_invitation(self):
        candidate = Owner.objects.create_user(
            username="new.member",
            email="new.member@example.com",
            password="password123",
        )
        self.login(self.owner)
        response = self.client.post(
            self.invite_url(),
            data={"username_or_email": candidate.email},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AccountInvitation.objects.filter(
                account=self.shared_account,
                invited_user=candidate,
                invited_by=self.owner,
                status=AccountInvitation.Status.PENDING,
            ).exists()
        )

    def test_member_cannot_create_invitation(self):
        self.login(self.member)
        response = self.client.post(
            self.invite_url(),
            data={"username_or_email": self.outsider.username},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(AccountInvitation.objects.filter(invited_user=self.outsider).exists())

    def test_outsider_cannot_create_invitation(self):
        self.login(self.outsider)
        response = self.client.post(
            self.invite_url(),
            data={"username_or_email": "someone@example.com"},
        )
        self.assertEqual(response.status_code, 404)

    def test_invited_user_sees_pending_invitation(self):
        self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        response = self.client.get(reverse("finance:invitation-list"))
        self.assertContains(response, "Shared wallet")

    def test_non_invited_user_does_not_see_invitation(self):
        self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.member)
        response = self.client.get(reverse("finance:invitation-list"))
        self.assertNotContains(response, "Shared wallet")

    def test_invited_user_can_accept_invitation(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        response = self.client.post(self.invitation_accept_url(invitation))
        self.assertEqual(response.status_code, 302)

    def test_accept_creates_membership(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        self.client.post(self.invitation_accept_url(invitation))
        self.assertTrue(
            AccountMembership.objects.filter(
                account=self.shared_account,
                user=self.outsider,
                role=AccountMembership.Role.MEMBER,
            ).exists()
        )

    def test_accepted_invitation_becomes_accepted(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        self.client.post(self.invitation_accept_url(invitation))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AccountInvitation.Status.ACCEPTED)

    def test_invited_user_can_reject_invitation(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        response = self.client.post(self.invitation_reject_url(invitation))
        self.assertEqual(response.status_code, 302)

    def test_reject_does_not_create_membership(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        self.client.post(self.invitation_reject_url(invitation))
        self.assertFalse(
            AccountMembership.objects.filter(
                account=self.shared_account, user=self.outsider
            ).exists()
        )

    def test_rejected_invitation_becomes_rejected(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.outsider)
        self.client.post(self.invitation_reject_url(invitation))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AccountInvitation.Status.REJECTED)

    def test_other_user_cannot_accept_someone_elses_invitation(self):
        invitee = Owner.objects.create_user(username="invitee", password="password123")
        invitation = self.create_pending_invitation(invited_user=invitee)
        self.login(self.outsider)
        response = self.client.post(self.invitation_accept_url(invitation))
        self.assertEqual(response.status_code, 404)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AccountInvitation.Status.PENDING)

    def test_other_user_cannot_reject_someone_elses_invitation(self):
        invitee = Owner.objects.create_user(username="invitee", password="password123")
        invitation = self.create_pending_invitation(invited_user=invitee)
        self.login(self.outsider)
        response = self.client.post(self.invitation_reject_url(invitation))
        self.assertEqual(response.status_code, 404)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, AccountInvitation.Status.PENDING)

    def test_cannot_invite_yourself(self):
        self.login(self.owner)
        self.client.post(self.invite_url(), data={"username_or_email": self.owner.username})
        self.assertFalse(
            AccountInvitation.objects.filter(
                account=self.shared_account, invited_user=self.owner
            ).exists()
        )

    def test_cannot_invite_existing_member(self):
        self.login(self.owner)
        self.client.post(self.invite_url(), data={"username_or_email": self.member.email})
        self.assertFalse(
            AccountInvitation.objects.filter(
                account=self.shared_account, invited_user=self.member
            ).exists()
        )

    def test_duplicate_pending_invitation_is_not_created(self):
        invitation = self.create_pending_invitation(invited_user=self.outsider)
        self.login(self.owner)
        self.client.post(self.invite_url(), data={"username_or_email": self.outsider.email})
        self.assertEqual(
            AccountInvitation.objects.filter(
                account=self.shared_account,
                invited_user=self.outsider,
                status=AccountInvitation.Status.PENDING,
            ).count(),
            1,
        )
        self.assertTrue(AccountInvitation.objects.filter(pk=invitation.pk).exists())

    def test_member_can_create_transaction_in_shared_account(self):
        self.login(self.member)
        response = self.client.post(
            reverse("finance:transaction-create"),
            data={
                "amount": "100.00",
                "description": "Shared groceries",
                "date": timezone.now().date(),
                "category": self.category_expense.pk,
                "account": self.shared_account.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Transaction.objects.filter(description="Shared groceries").exists())

    def test_transaction_created_by_equals_member(self):
        self.login(self.member)
        self.client.post(
            reverse("finance:transaction-create"),
            data={
                "amount": "100.00",
                "description": "Member created",
                "date": timezone.now().date(),
                "category": self.category_expense.pk,
                "account": self.shared_account.pk,
            },
        )
        transaction = Transaction.objects.get(description="Member created")
        self.assertEqual(transaction.created_by, self.member)

    def test_member_transaction_changes_shared_account_balance(self):
        self.login(self.member)
        self.client.post(
            reverse("finance:transaction-create"),
            data={
                "amount": "100.00",
                "description": "Balance change",
                "date": timezone.now().date(),
                "category": self.category_expense.pk,
                "account": self.shared_account.pk,
            },
        )
        self.shared_account.refresh_from_db()
        self.assertEqual(self.shared_account.balance, Decimal("900.00"))

    def test_owner_sees_changed_balance(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Shared expense",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.shared_account,
            created_by=self.member,
        )
        self.login(self.owner)
        response = self.client.get(reverse("finance:account-list"))
        self.assertContains(response, "900.00")

    def test_member_sees_changed_balance(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Shared expense",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.shared_account,
            created_by=self.member,
        )
        self.login(self.member)
        response = self.client.get(reverse("finance:account-list"))
        self.assertContains(response, "900.00")

    def test_outsider_cannot_create_transaction_using_shared_account_id(self):
        self.login(self.outsider)
        response = self.client.post(
            reverse("finance:transaction-create"),
            data={
                "amount": "100.00",
                "description": "Tampered",
                "date": timezone.now().date(),
                "category": self.category_expense.pk,
                "account": self.shared_account.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Transaction.objects.filter(description="Tampered").exists())

    def test_member_sees_shared_transactions(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Visible shared transaction",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.shared_account,
            created_by=self.owner,
        )
        self.login(self.member)
        response = self.client.get(reverse("finance:transaction-list"))
        self.assertContains(response, "Visible shared transaction")

    def test_outsider_does_not_see_shared_transactions(self):
        Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Hidden shared transaction",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.shared_account,
            created_by=self.owner,
        )
        self.login(self.outsider)
        response = self.client.get(reverse("finance:transaction-list"))
        self.assertNotContains(response, "Hidden shared transaction")

    def test_direct_url_guessing_does_not_bypass_membership(self):
        transaction = Transaction.objects.create(
            amount=Decimal("100.00"),
            description="Guessed transaction",
            date=timezone.now().date(),
            category=self.category_expense,
            account=self.shared_account,
            created_by=self.owner,
        )
        self.login(self.outsider)
        response = self.client.get(
            reverse("finance:transaction-update", args=[transaction.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_manual_post_with_foreign_account_id_does_not_bypass_permissions(self):
        private_account = Account.objects.create(
            name="Private",
            account_type="cash",
            balance=Decimal("500.00"),
            owner=self.outsider,
        )
        self.login(self.member)
        response = self.client.post(
            reverse("finance:transaction-create"),
            data={
                "amount": "50.00",
                "description": "Foreign account tamper",
                "date": timezone.now().date(),
                "category": self.category_expense.pk,
                "account": private_account.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Transaction.objects.filter(description="Foreign account tamper").exists()
        )

    def test_only_owner_can_manage_memberships(self):
        self.login(self.member)
        response = self.client.get(self.members_url())
        self.assertEqual(response.status_code, 404)

        response = self.client.post(self.remove_member_url(self.member_membership))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            AccountMembership.objects.filter(pk=self.member_membership.pk).exists()
        )
