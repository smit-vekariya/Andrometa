from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
from account.models import BondUser

class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
                     'self', null=True, blank=True,
                     on_delete=models.CASCADE, related_name='subfolders'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'parent', 'name')

    def get_full_path(self):
        # Returns '/Projects/Design/'
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(parts)) + '/'

    def __str__(self):
        return self.get_full_path()


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='files')

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

    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name='files')

    # File Metadata
    local_media_id = models.CharField(max_length=255, help_text="ID from phone gallery")
    device_id = models.CharField(max_length=255, help_text="Originating device ID")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, help_text="IMAGE, VIDEO, etc.")

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
        ]
        unique_together = [['content_type', 'object_id', 'local_media_id', 'device_id']]

    def __str__(self):
        return f"{self.file_name} ({self.status})"



