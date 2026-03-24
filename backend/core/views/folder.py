from manager.base_view import BaseModelViewSet
from core.models import Folder, File
from core.serializers import FolderSerializer, FileSerializer, FileListSerializer
from manager.manager import HttpsAppResponse


class FolderViewSet(BaseModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    search_fields = ['name']
    ordering_fields = ('name', 'created_at')

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            folder_id = request.query_params.get('folder_id')

            if folder_id:
                try:
                    current_folder = Folder.objects.get(id=folder_id, user=user)
                except Folder.DoesNotExist:
                    return HttpsAppResponse.send([], 0, "Folder not found", status_code=404)
            else:
                current_folder = None

            subfolders = Folder.objects.filter(
                user=user,
                parent=current_folder,
                is_deleted=False
            ).order_by('name')

            subfolder_data = FolderSerializer(subfolders, many=True).data

            files_qs = File.objects.filter(
                folder=current_folder,
                user=user,
                is_deleted=False
            ).order_by('-created_at')

            # Apply pagination ONLY to files
            page = self.paginate_queryset(files_qs)

            if page is not None:
                file_serializer = FileListSerializer(page, many=True)
                paginated_files = self.get_paginated_response(file_serializer.data).data
            else:
                file_serializer = FileListSerializer(files_qs, many=True)
                paginated_files = file_serializer.data

            return HttpsAppResponse.send(
                {
                    "subfolders": subfolder_data,
                    "files": paginated_files
                },
                1,
                "Success",
                status_code=200
            )

        except Exception as e:
            return HttpsAppResponse.exception(str(e))
