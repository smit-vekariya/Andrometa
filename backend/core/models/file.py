
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from account.models import CustomUser
from manager.base_model import BaseModel
from .folder import Folder

class File(BaseModel):

    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name='files')

    # Generic FK — points to GoogleDriveAccount, OneDriveAccount, DropboxAccount, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    storage_account = GenericForeignKey('content_type', 'object_id')

    # File metadata
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, help_text="IMAGE, VIDEO, DOC, etc.")
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    size_bytes = models.BigIntegerField(default=0)

    # Storage provider pointers
    remote_file_id = models.CharField(max_length=255, help_text="Provider's file ID (Drive ID, OneDrive ID, etc.)")
    remote_file_path = models.TextField(help_text="Full path on provider, e.g. /CloudMerge/Photos/img.jpg")
    remote_view_url = models.URLField(null=True, blank=True, help_text="Direct view/preview URL from provider")
    remote_download_url = models.URLField(max_length=500, null=True, blank=True, help_text="Direct download URL")
    remote_thumbnail_url = models.URLField(max_length=500, null=True, blank=True, help_text="Thumbnail/preview for images & videos")

    # Origin tracking
    local_media_id = models.CharField(max_length=255, null=True, blank=True, help_text="ID from phone gallery")
    device_id = models.CharField(max_length=255, null=True, blank=True, help_text="Originating device ID")


    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id', 'remote_file_id']),
            models.Index(fields=['user', 'folder']),
            models.Index(fields=['local_media_id', 'device_id']),
        ]
        unique_together = [
            ['content_type', 'object_id', 'remote_file_id'],         # one remote file = one record
            ['content_type', 'object_id', 'local_media_id', 'device_id'],  # no duplicate uploads from same device
        ]

    def __str__(self):
        return f"{self.file_name} → {self.remote_file_path} "



