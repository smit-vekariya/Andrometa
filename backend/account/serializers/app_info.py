from rest_framework import serializers
from account.models import AppInfo, AppReport

class AppInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppInfo
        fields = ['device', 'version', 'url', 'force_update']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['url'] is None:
            ret['url'] = ""
        return ret

class AppReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppReport
        fields = '__all__'
