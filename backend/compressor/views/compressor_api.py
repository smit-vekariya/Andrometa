from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsAuthenticatedOrHasDeviceID
from django.http import FileResponse
from manager.manager import HttpsAppResponse
from compressor.serializers import CompressionSerializer
from compressor.views import COMPRESSOR_FORMATS
from compressor.views.image_compressor import compress_image
from PIL import Image


class ImageCompressorView(APIView):
    """
    API endpoint for image compression.

    POST /compressor/compress/
    - file: The file(s) to compress (multipart)
    - mode: less, recommended, extreme, lossless, target_size, target_percent, quality
    - value: numeric value for size, percent, or quality (if applicable)
    - unit: KB or MB (if applicable)

    Returns the compressed file(s) as a downloadable response.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrHasDeviceID]

    def post(self, request):
        try:
            serializer = CompressionSerializer(data=request.data)
            if not serializer.is_valid():
                errors = serializer.errors
                first_error_key = next(iter(errors))
                try:
                    first_error_msg = errors[first_error_key][0]
                except Exception:
                    first_error_msg = str(errors[first_error_key])
                return HttpsAppResponse.send([], 0, str(first_error_msg))

            validated_data = serializer.validated_data
            files = validated_data['file']
            mode = validated_data['mode']
            value = validated_data.get('value', None)
            unit = validated_data.get('unit', 'KB')

            output_buffer, output_filename, content_type = compress_image(files, mode, value, unit)

            response = FileResponse(
                output_buffer,
                content_type=content_type,
                as_attachment=True,
                filename=output_filename,
            )
            return response

        except Exception as e:
            return HttpsAppResponse.exception(str(e))

class CheckAvailabilityView(APIView):
    """
    API endpoint to check supported formats for compressor.

    GET /compressor/availability/
    - file_type: (optional) The source file format to check.

    Returns a list of supported formats or a boolean if specific format is requested.
    """
    permission_classes = [IsAuthenticatedOrHasDeviceID]

    def get(self, request):
        try:
            file_type = request.query_params.get("file_type")
            if file_type:
                file_type = file_type.strip().lower()
                supported_targets = COMPRESSOR_FORMATS.get(file_type, [])
            else:
                supported_targets = COMPRESSOR_FORMATS
            return HttpsAppResponse.send(supported_targets, 1, "Success")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

