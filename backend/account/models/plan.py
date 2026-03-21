import uuid
from django.db import models

class Plan(models.Model):
    """
    Immutable plan definitions. Never edit — create new versions instead.
    Old subscriptions reference the plan snapshot they signed up with.
    """
    TIER_FREEMIUM = "freemium"
    TIER_BASIC    = "basic"
    TIER_PREMIUM  = "premium"
    TIER_CHOICES  = [
        (TIER_FREEMIUM, "Freemium"),
        (TIER_BASIC,    "Basic"),
        (TIER_PREMIUM,  "Premium"),
    ]

    CYCLE_MONTHLY = "monthly"
    CYCLE_YEARLY  = "yearly"
    CYCLE_CHOICES = [
        (CYCLE_MONTHLY, "Monthly"),
        (CYCLE_YEARLY,  "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    billing_cycle   = models.CharField(max_length=10, choices=CYCLE_CHOICES)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    tax_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Feature flags — snapshot what the user paid for
    has_ads = models.BooleanField(default=True)
    max_accounts = models.IntegerField(default=3)        # -1 = unlimited
    folder_sharing = models.BooleanField(default=False)
    password_protected = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One active plan per tier+cycle combo
        unique_together = [("tier", "billing_cycle", "is_active")]
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.billing_cycle}) — ${self.price}"

    @property
    def is_unlimited_accounts(self):
        return self.max_accounts == -1