from manager.base_serializer import BaseModelSerializer
from core.models import GoogleDriveAccount


class GoogleDriveAccountSerializer(BaseModelSerializer):

    class Meta(BaseModelSerializer.Meta):
        model = GoogleDriveAccount
        fields = [
            'id', 'email',
            'total_storage', 'app_used_storage',
            'user_used_storage', 'remaining_storage',
            'is_active', 'is_deleted', 'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = [
            'id', 'email',
            'total_storage', 'app_used_storage',
            'user_used_storage', 'remaining_storage',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]


class GoogleDriveAccountDetailSerializer(BaseModelSerializer):
    """Admin/internal use — includes tokens."""

    class Meta(BaseModelSerializer.Meta):
        model = GoogleDriveAccount
        fields = [
            'id', 'email',
            'access_token', 'refresh_token', 'token_uri',
            'client_id', 'client_secret', 'expiry',
            'total_storage', 'app_used_storage',
            'user_used_storage', 'remaining_storage',
            'is_active', 'is_deleted', 'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = fields