from rest_framework import serializers
from manager.base_serializer import BaseModelSerializer
from core.models import Folder


class FolderSerializer(BaseModelSerializer):
    full_path = serializers.SerializerMethodField()
    sub_folders = serializers.SerializerMethodField()

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_sub_folders(self, obj):
        return FolderSerializer(
            obj.sub_folders.filter(is_deleted=False), many=True
        ).data

    class Meta(BaseModelSerializer.Meta):
        model = Folder
        fields = [
            'id', 'name', 'parent', 'full_path', 'sub_folders',
            'is_active', 'is_deleted', 'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = ['id', 'full_path', 'sub_folders']
