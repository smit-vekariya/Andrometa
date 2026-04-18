from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from manager.manager import HttpsAppResponse
from converter.views import CONVERTER_MAP, AVAILABLE_FORMATS
from converter.serializers import FileConversionSerializer, FormatCheckSerializer


class FileConverterView(APIView):
    """
    API endpoint for file conversion.

    POST /converter/convert/
    - file: The file to convert (multipart)
    - file_type_from: Source format (e.g. pdf, jpeg, png, webp)
    - file_type_to: Target format (e.g. docx, pdf, png, jpeg, webp)

    Returns the converted file as a downloadable response.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = FileConversionSerializer(data=request.data)
            if not serializer.is_valid():
                errors = serializer.errors
                # Extract the first error message formatted as a string
                first_error_key = next(iter(errors))
                first_error_msg = errors[first_error_key][0]
                return HttpsAppResponse.send([], 0, str(first_error_msg))

            files = request.FILES.getlist('file')
            if len(files) > 1:
                return HttpsAppResponse.send([], 0, "Only one file is allowed.")

            file = files[0]
            file_type_from = serializer.validated_data['file_type_from']
            file_type_to = serializer.validated_data['file_type_to']

            # Look up the converter function
            converter_key = (file_type_from, file_type_to)
            converter_function = CONVERTER_MAP.get(converter_key)

            # Perform conversion
            output_buffer, output_filename, content_type = converter_function(file)

            # Return converted file
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
    API endpoint to check supported target formats for a given source format.

    POST /converter/availability/
    - file_type: The source file format (e.g. pdf, jpeg, png, webp)

    Returns a list of supported target formats.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = FormatCheckSerializer(data=request.data)
            if not serializer.is_valid():
                errors = serializer.errors
                first_error_key = next(iter(errors))
                first_error_msg = errors[first_error_key][0]
                return HttpsAppResponse.send([], 0, str(first_error_msg))

            file_type = serializer.validated_data['file_type'].strip().lower()
            supported_targets = AVAILABLE_FORMATS.get(file_type, [])

            return HttpsAppResponse.send(supported_targets, 1, "Success")

        except Exception as e:
            return HttpsAppResponse.exception(str(e))
