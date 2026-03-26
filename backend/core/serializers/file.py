from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from manager.base_serializer import BaseModelSerializer
from core.models import File


class FileUploadSerializer(serializers.Serializer):
    folder_id = serializers.UUIDField(required=False, allow_null=True)
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)
    device_id = serializers.CharField(required=False, allow_blank=True)


class FileSerializer(BaseModelSerializer):
    storage_content_type = serializers.CharField(write_only=True, help_text="e.g. 'core.googledriveaccount'")
    storage_object_id = serializers.CharField(write_only=True)

    storage_account_repr = serializers.SerializerMethodField()

    def get_storage_account_repr(self, obj):
        account = obj.storage_account
        if not account:
            return None
        return {
            "type": obj.content_type.model,
            "id": str(obj.object_id),
            "email": getattr(account, 'email', None),
        }

    class Meta(BaseModelSerializer.Meta):
        model = File
        fields = [
            'id', 'user', 'folder',
            'storage_content_type', 'storage_object_id', 'storage_account_repr',
            'file_name', 'file_type', 'mime_type', 'size_bytes',
            'remote_file_id', 'remote_file_path', 'remote_view_url',
            'local_media_id', 'device_id',
            'is_active', 'is_deleted', 'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = ['id', 'user', 'storage_account_repr']


class FileListSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = File
        fields = [
            'id',
            'file_name', 'file_type', 'size_bytes',
            'remote_file_id', 'remote_view_url', 'remote_thumbnail_url',
            'created_at',
        ]
        read_only_fields = ['id']