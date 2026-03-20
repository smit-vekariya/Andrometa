from rest_framework.decorators import action
from rest_framework.response import Response
from manager.base_view import BaseModelViewSet
from core.models import Folder, File
from core.serializers import FolderSerializer, FileSerializer


class FolderViewSet(BaseModelViewSet):
    serializer_class = FolderSerializer
    search_fields = ['name']
    ordering_fields = ('name', 'created_at')

    def get_queryset(self):
        return Folder.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).select_related('parent')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='root')
    def root_folders(self, request):
        """Returns only top-level folders (no parent)."""
        qs = self.get_queryset().filter(parent=None)
        serializer = self.get_serializer(qs, many=True)
        return Response({"data": serializer.data, "status": 1})

