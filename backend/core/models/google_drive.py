
from django.db import models
from account.models import BondUser
from manager.base_model import BaseModel

class GoogleDriveAccount(BaseModel):
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='google_accounts')
    email = models.EmailField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    expiry = models.DateTimeField()
    total_storage = models.BigIntegerField(default=0)
    app_used_storage = models.BigIntegerField(default=0)
    user_used_storage = models.BigIntegerField(default=0)
    remaining_storage = models.BigIntegerField(default=0)

    def __str__(self):
        return f"Google: {self.email}"