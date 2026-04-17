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
        
        for file in value:
            if not file.name.lower().endswith('.pdf'):
                raise serializers.ValidationError(f"File '{file.name}' is not a valid PDF.")
        
        return value
