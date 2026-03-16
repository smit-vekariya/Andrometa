from rest_framework.serializers import ModelSerializer
from postoffice.models import EmailLog


class EmailLogSerializer(ModelSerializer):
    class Meta:
        model =  EmailLog
        fields = "__all__"