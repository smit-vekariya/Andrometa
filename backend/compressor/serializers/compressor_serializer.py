from rest_framework import serializers

class CompressionSerializer(serializers.Serializer):
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
