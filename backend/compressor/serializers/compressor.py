from django.conf import settings
from rest_framework import serializers
from PIL import Image

class CompressionSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        error_messages={'required': 'At least one file is required.'}
    )
    mode = serializers.ChoiceField(
        choices=['less', 'recommended', 'extreme', 'target_size', 'target_percent', 'quality'],
        required=True,
        error_messages={'required': 'mode is required.', 'invalid_choice': 'Invalid compression mode.'}
    )
    # Unit for Target File Size
    unit = serializers.ChoiceField(
        choices=['KB', 'MB'],
        required=False,
        default='KB'
    )
    value = serializers.FloatField(required=False)

    def validate_file(self, value):
        # Check number of files
        if len(value) > settings.MAX_COMPRESS_FILE_COUNT:
            raise serializers.ValidationError(f"You can compress a maximum of {settings.MAX_COMPRESS_FILE_COUNT} images at once.")

        # Check combined size
        total_size = sum(file.size for file in value)
        if total_size > settings.COMPRESSOR_DATA_UPLOAD_MAX_MEMORY_SIZE:
            limit_mb = settings.COMPRESSOR_DATA_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
            raise serializers.ValidationError(f"Total size of all files exceeds the allowed limit of {limit_mb:.1f}MB.")

        # Check each file is a valid image
        for file in value:
            try:
                file.seek(0)
                img = Image.open(file)
                img.verify()
            except Exception:
                raise serializers.ValidationError(f"File '{file.name}' is not a valid image or unsupported format.")
            finally:
                file.seek(0)

        return value

    def validate(self, attrs):
        mode = attrs.get('mode')
        value = attrs.get('value')

        # validate if value required
        if mode in ['target_size', 'target_percent', 'quality']:
            if value is None:
                raise serializers.ValidationError(f"value is required for mode '{mode}'.")

            if mode == 'target_percent' and not (1 <= value <= 100):
                raise serializers.ValidationError("target_percent must be between 1 and 100.")

            if mode == 'quality' and not (1 <= value <= 100):
                raise serializers.ValidationError("quality must be between 1 and 100.")

            if mode == 'target_size' and value <= 0:
                raise serializers.ValidationError("target_size must be greater than 0.")

        return attrs

