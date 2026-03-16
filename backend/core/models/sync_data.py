from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SyncData(models.Model):
    """Tracks synchronization status of gallery media to cloud storage."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SYNCED', 'Synced'),
        ('FAILED', 'Failed'),
    ]

    # Generic FK to link to either GoogleDriveAccount or OneDriveAccount
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    storage_account = GenericForeignKey('content_type', 'object_id')

    # File Metadata
    local_media_id = models.CharField(max_length=255, help_text="ID from phone gallery")
    device_id = models.CharField(max_length=255, help_text="Originating device ID")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, help_text="IMAGE, VIDEO, etc.")
    checksum = models.CharField(max_length=255, db_index=True, help_text="MD5/SHA hash of file content")

    # Sync Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    remote_id = models.CharField(max_length=255, null=True, blank=True, help_text="Cloud file ID")
    last_sync_attempt = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['local_media_id', 'device_id']),
            models.Index(fields=['checksum']),
        ]
        unique_together = [['content_type', 'object_id', 'local_media_id', 'device_id']]

    def __str__(self):
        return f"{self.file_name} ({self.status})"



