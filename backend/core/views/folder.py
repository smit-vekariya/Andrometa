from rest_framework.decorators import action
from rest_framework.response import Response
from manager.base_view import BaseModelViewSet
from core.models import Folder, File
from core.serializers import FolderSerializer, FileSerializer


class FolderViewSet(BaseModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    search_fields = ['name']
    ordering_fields = ('name', 'created_at')
