from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from manager.base_serializer import BaseModelSerializer
from core.models import File


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

    def validate(self, attrs):
        attrs = super().validate(attrs)

        raw_ct = attrs.pop('storage_content_type', None)
        object_id = attrs.pop('storage_object_id', None)

        if raw_ct and object_id:
            try:
                app_label, model = raw_ct.lower().split('.')
                ct = ContentType.objects.get(app_label=app_label, model=model)
                model_class = ct.model_class()

                account = model_class.objects.get(id=object_id)
                # Ensure account belongs to request user
                if account.user != self.context['request'].user:
                    raise serializers.ValidationError("Storage account not found.")

                attrs['content_type'] = ct
                attrs['object_id'] = account.pk

            except (ValueError, ContentType.DoesNotExist, Exception):
                raise serializers.ValidationError("Invalid storage account.")

        return attrs

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