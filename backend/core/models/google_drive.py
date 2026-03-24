
from django.db import models
from account.models import CustomUser
from manager.base_model import BaseModel
from manager.manager import encrypt_token, decrypt_token

class GoogleDriveAccount(BaseModel):
    email = models.EmailField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    expiry = models.DateTimeField()
    root_folder_id = models.CharField(max_length=255)
    total_storage = models.BigIntegerField(default=0, help_text="Total storage in bytes")
    app_used_storage = models.BigIntegerField(default=0, help_text="Used storage in bytes")
    user_used_storage = models.BigIntegerField(default=0, help_text="Used storage in bytes")
    remaining_storage = models.BigIntegerField(default=0, help_text="Remaining storage in bytes")
    priority = models.PositiveIntegerField(default=0, help_text="Lower = higher priority")

    def save(self, *args, **kwargs):
        self.access_token = encrypt_token(self.access_token)
        self.refresh_token = encrypt_token(self.refresh_token)
        self.client_secret = encrypt_token(self.client_secret)
        super().save(*args, **kwargs)

    def get_access_token(self):
        return decrypt_token(self.access_token)

    def get_refresh_token(self):
        return decrypt_token(self.refresh_token)

    def get_client_secret(self):
        return decrypt_token(self.client_secret)


    def __str__(self):
        return f"Google: {self.email}"

    class Meta:
        ordering = ['priority']

    @staticmethod
    def _format_bytes(b: int) -> str:
        if b < 1024:
            return f"{b} B"
        elif b < 1024 ** 2:
            return f"{round(b / 1024, 2)} KB"
        elif b < 1024 ** 3:
            return f"{round(b / (1024 ** 2), 2)} MB"
        elif b < 1024 ** 4:
            return f"{round(b / (1024 ** 3), 2)} GB"
        else:
            return f"{round(b / (1024 ** 4), 2)} TB"

    def storage_display(self) -> dict:
        return {
            "total_storage":     self._format_bytes(self.total_storage),
            "user_used_storage": self._format_bytes(self.user_used_storage),
            "app_used_storage":  self._format_bytes(self.app_used_storage),
            "remaining_storage": self._format_bytes(self.remaining_storage),
        }