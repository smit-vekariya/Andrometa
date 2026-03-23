from manager.base_view import BaseModelViewSet
from core.models import Folder, File
from core.serializers import FolderSerializer, FileSerializer


class FolderViewSet(BaseModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    search_fields = ['name']
    ordering_fields = ('name', 'created_at')

    def get_queryset(self):
        folder_id = self.request.query_params.get('folder_id')
        qs = super().get_queryset().filter(user=self.request.user)
        if folder_id:
            return qs.filter(parent_id=folder_id)
        return qs.filter(parent=None)
