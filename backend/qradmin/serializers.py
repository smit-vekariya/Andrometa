from rest_framework import serializers
from qradmin.models import QRCode, QRBatch


class QRBatchSerializers(serializers.ModelSerializer):
    class Meta:
        model= QRBatch
        fields = '__all__'

        # def create(self, validated_data):
            # return super().create(*validated_data)


class QRCodeSerializers(serializers.ModelSerializer):
    batch__batch_number = serializers.CharField()

    class Meta:
        model = QRCode
        fields = ["qr_number", "qr_code", "point", "batch__batch_number"]

    def create(self, validated_data):
        validated_data["batch"] = QRBatch.objects.get(batch_number=validated_data["batch__batch_number"])
        validated_data.pop("batch__batch_number")
        QRCode.objects.create(**validated_data)


class QRBatchListSerializers(serializers.ModelSerializer):
    class Meta:
        model = QRBatch
        fields ='__all__'


class QRCodeListSerializers(serializers.ModelSerializer):
    batch__batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    used_by__mobile = serializers.CharField(source='used_by.mobile', read_only=True)
    used_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = QRCode
        fields = ["id","qr_number","qr_code","batch__batch_number","is_disabled", "point","used_on","used_by__mobile"]