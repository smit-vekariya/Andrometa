from django.conf import settings
from rest_framework import serializers
from converter.views import CONVERTER_MAP

class FileConversionSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=True,
        error_messages={'required': 'File is required.', 'empty': 'File is required.', 'no_name': 'File is required.'}
    )
    file_type_from = serializers.CharField(
        required=True,
        error_messages={'required': 'file_type_from is required.', 'blank': 'file_type_from is required.'}
    )
    file_type_to = serializers.CharField(
        required=True,
        error_messages={'required': 'file_type_to is required.', 'blank': 'file_type_to is required.'}
    )

    def validate_file(self, value):
        max_size = settings.CONVERTOR_DATA_UPLOAD_MAX_MEMORY_SIZE
        if value.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise serializers.ValidationError(f"File size exceeds the limit of {max_size_mb:.1f} MB.")
        return value

    def validate(self, attrs):
        # Check for multiple files
        request = self.context.get('request')
        if request and request.FILES:
            files = request.FILES.getlist('file')
            if len(files) > 1:
                raise serializers.ValidationError({"file": "Only one file is allowed."})

        file_type_from = attrs.get('file_type_from', '').strip().lower()
        file_type_to = attrs.get('file_type_to', '').strip().lower()

        # Update attrs with cleaned data
        attrs['file_type_from'] = file_type_from
        attrs['file_type_to'] = file_type_to

        if file_type_from == file_type_to:
            raise serializers.ValidationError("file_type_from and file_type_to cannot be the same.")

        converter_key = (file_type_from, file_type_to)
        if converter_key not in CONVERTER_MAP:
            supported_conversions = ', '.join(
                [f"{src} → {dst}" for src, dst in CONVERTER_MAP.keys()]
            )
            raise serializers.ValidationError(
                f"Unsupported conversion: {file_type_from} to {file_type_to}. "
                f"Supported conversions: {supported_conversions}"
            )

        return attrs