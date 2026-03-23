from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from manager.base_view import BaseModelViewSet
from core.models import File, Folder
from core.serializers import FileSerializer, FileUploadSerializer
from manager.manager import HttpsAppResponse
from manager.manager import custom_response_errors
from packages.google_drive.smart_upload import SmartUploadService, SmartUploadServiceError


class FileViewSet(BaseModelViewSet):
    queryset = File.objects.all().select_related('folder', 'content_type')
    serializer_class = FileSerializer
    search_fields = ['file_name', 'file_type']
    ordering_fields = ('file_name', 'size_bytes', 'created_at')

    def get_queryset(self):
        folder_id = self.request.query_params.get('folder_id')
        qs = super().get_queryset()
        if folder_id:
            return qs.filter(folder_id=folder_id)
        return qs.filter(folder=None)

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        try:
            serializer = FileUploadSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            data = serializer.validated_data
            raw_files = data['files']
            folder_id = data.get('folder_id')
            device_id = data.get('device_id')
            folder = None

            if folder_id:
                try:
                    folder = Folder.objects.get(id=folder_id, user=request.user, is_deleted=False)
                except Folder.DoesNotExist:
                    return HttpsAppResponse.send([], 0, "Folder not found.")

            try:
                service = SmartUploadService(user=request.user)
                result  = service.upload_many(folder=folder, files=raw_files, device_id=device_id)
            except SmartUploadServiceError as e:
                return HttpsAppResponse.send([], 0, str(e.as_dict()))

            data = {
                "uploaded": FileSerializer(result["uploaded"], many=True).data,
                "failed":   result["failed"],
                "total":    len(raw_files),
                "success_count": len(result["uploaded"]),
                "fail_count":    len(result["failed"]),
            }
            return HttpsAppResponse.send([], 1, "File uploaded successfully.", status_code=status.HTTP_201_CREATED)
        except Exception as e:
            return HttpsAppResponse.exception(str(e))