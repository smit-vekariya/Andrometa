from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from manager.manager import HttpsAppResponse
from merger.serializers import PDFMergerSerializer
from merger.views.pdf_merger import merge_pdfs


class PDFMergerView(APIView):
    """
    API endpoint for merging multiple PDF files.

    POST /merger/merge/
    - file: Multiple PDF files (multipart)

    Returns the merged PDF file as a downloadable response.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Use getlist to handle multiple files in the 'file' field
            files = request.FILES.getlist('file')
            
            serializer = PDFMergerSerializer(data={'file': files})
            if not serializer.is_valid():
                errors = serializer.errors
                first_error_key = next(iter(errors))
                try:
                    first_error_msg = errors[first_error_key][0]
                except Exception:
                    first_error_msg = str(errors[first_error_key])
                return HttpsAppResponse.send([], 0, str(first_error_msg))

            validated_files = serializer.validated_data['file']

            # Perform merge
            output_buffer, output_filename, content_type = merge_pdfs(validated_files)

            # Return merged file
            response = FileResponse(
                output_buffer,
                content_type=content_type,
                as_attachment=True,
                filename=output_filename,
            )
            return response

        except Exception as e:
            return HttpsAppResponse.exception(str(e))
