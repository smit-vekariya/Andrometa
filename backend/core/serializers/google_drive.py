from manager.base_serializer import BaseModelSerializer
from core.models import GoogleDriveAccount
from rest_framework import serializers


class GoogleDriveAccountSerializer(BaseModelSerializer):
    storage_display = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = GoogleDriveAccount
        fields = ['id', 'email', 'is_active', 'storage_display', 'type']
        read_only_fields = ['id', 'email', 'type']

    def get_storage_display(self, obj):
        return obj.storage_display()

    def get_type(self, obj):
        return "google"