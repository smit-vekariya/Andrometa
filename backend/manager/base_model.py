import uuid
from django.db import models
from django.utils import timezone
from account.models import BondUser

class BaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s')
    created_by = models.ForeignKey(
        BondUser,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created_by",
        null=True,
    )
    updated_by = models.ForeignKey(
        BondUser,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated_by",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        BondUser,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deleted_by",
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def soft_delete(self, user: BondUser = None) -> None:
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
