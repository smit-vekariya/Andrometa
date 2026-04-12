from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from manager.manager import HttpsAppResponse
from converter.views import CONVERTER_MAP
from converter.serializers import FileConversionSerializer


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
            file_type_from = serializer.validated_data['file_type_from']
            file_type_to = serializer.validated_data['file_type_to']

            # Look up the converter function
            converter_key = (file_type_from, file_type_to)
            converter_function = CONVERTER_MAP.get(converter_key)

            # Perform conversion
            if converter_function.__name__ == 'convert_image_to_pdf':
                output_buffer, output_filename, content_type = converter_function(files)
            else:
                output_buffer, output_filename, content_type = converter_function(files[0])

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
