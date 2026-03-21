import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from account.models import Plan


class UserSubscription(models.Model):
    """
    Active or historical subscription record per user.
    Stores a snapshot of the plan features at purchase time so plan
    edits never retroactively affect existing subscribers.
    """
    STATUS_ACTIVE    = "active"
    STATUS_EXPIRED   = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES   = [
        (STATUS_ACTIVE,    "Active"),
        (STATUS_EXPIRED,   "Expired"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,      # never delete a plan that has subs
        related_name="subscriptions"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    started_on = models.DateTimeField(default=timezone.now)
    expires_on = models.DateTimeField()
    cancelled_on = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    # These never change even if Plan is updated later.
    snapshot_tier = models.CharField(max_length=20)
    snapshot_price  = models.DecimalField(max_digits=8, decimal_places=2)
    snapshot_tax_price  = models.DecimalField(max_digits=8, decimal_places=2)
    snapshot_tax_rate = models.DecimalField(max_digits=8, decimal_places=2)
    snapshot_total_price  = models.DecimalField(max_digits=8, decimal_places=2)
    snapshot_has_ads = models.BooleanField()
    snapshot_max_accounts  = models.IntegerField()
    snapshot_folder_sharing  = models.BooleanField()
    snapshot_password_protected = models.BooleanField()
    snapshot_all_future_features= models.BooleanField()

    created_on  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_on"]

    def __str__(self):
        return f"{self.user} → {self.plan.name} [{self.status}]"

    def save(self, *args, **kwargs):
        # Auto-populate snapshot on first save
        if not self.snapshot_tier:
            self._take_snapshot()
        super().save(*args, **kwargs)

    def _take_snapshot(self):
        p = self.plan
        self.snapshot_tier = p.tier
        self.snapshot_price = p.price
        self.snapshot_has_ads = p.has_ads
        self.snapshot_max_accounts = p.max_accounts
        self.snapshot_folder_sharing = p.folder_sharing
        self.snapshot_password_protected = p.password_protected
        self.snapshot_all_future_features = p.all_future_features

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE and self.expires_on > timezone.now()

    # Convenience accessors always read from snapshot, not the live plan
    @property
    def can_add_account(self, current_count: int) -> bool:
        if self.snapshot_max_accounts == -1:
            return True
        return current_count < self.snapshot_max_accounts

    @property
    def show_ads(self):
        return self.snapshot_has_ads

    @property
    def can_share_folder(self):
        return self.snapshot_folder_sharing

    @property
    def can_password_protect(self):
        return self.snapshot_password_protected