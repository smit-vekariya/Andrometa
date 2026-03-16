from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from account.models import BondUser


class OneDriveAccount(models.Model):
    """Stores OneDrive OAuth credentials for a user."""
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='onedrive_accounts')
    email = models.EmailField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.CharField(max_length=255, default="https://login.microsoftonline.com/common/oauth2/v2.0/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    expiry = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OneDrive: {self.email}"