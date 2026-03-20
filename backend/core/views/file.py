from manager.base_view import BaseModelViewSet
from core.models import File
from core.serializers import FileSerializer


class FileViewSet(BaseModelViewSet):
    serializer_class = FileSerializer
    search_fields = ['file_name', 'file_type']
    ordering_fields = ('file_name', 'size_bytes', 'created_at')

    def get_queryset(self):
        qs = File.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).select_related('folder', 'content_type')

        folder_id = self.request.query_params.get('folder')
        if folder_id:
            qs = qs.filter(folder_id=folder_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)