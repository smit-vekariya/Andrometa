from django.conf import settings
from rest_framework import serializers

class PDFMergerSerializer(serializers.Serializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        error_messages={'required': 'At least two PDF files are required.'}
    )

    def validate_file(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least two PDF files are required to merge.")

        if len(value) > settings.MAX_MERGE_FILE_COUNT:
            raise serializers.ValidationError(f"You can merge a maximum of {settings.MAX_MERGE_FILE_COUNT} files at once.")

        total_size = sum(file.size for file in value)
        if total_size > settings.MERGER_DATA_UPLOAD_MAX_MEMORY_SIZE:
            limit_mb = settings.MERGER_DATA_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
            raise serializers.ValidationError(f"Total size of all files exceeds the allowed limit of {limit_mb:.1f}MB.")

        for file in value:
            if not file.name.lower().endswith('.pdf'):
                raise serializers.ValidationError(f"File '{file.name}' is not a valid PDF.")

        return value

