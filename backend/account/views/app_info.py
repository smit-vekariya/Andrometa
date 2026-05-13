from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from account.models import AppInfo, AppReport
from account.serializers import AppInfoSerializer
from datetime import datetime
from manager.manager import HttpsAppResponse


class AppInfoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            device_id = request.data.get("device_id")
            device_type = request.data.get("type")
            meta_data = request.data.get("meta_data")
            device_info = AppInfo.objects.get(device=device_type)
            report, created = AppReport.objects.get_or_create(
                device_id=device_id,
                device_name=device_info,
                defaults={'first_login_date': datetime.now(), 'last_login_date': datetime.now(), 'meta_data': meta_data}
            )
            if created:
                device_info.total_download += 1
                device_info.save()
            else:
                report.last_login_date = datetime.now()
                if meta_data:
                    report.meta_data = meta_data
                report.save()

            serializer = AppInfoSerializer(device_info)

            return HttpsAppResponse.send(data=[serializer.data], status=1, message="App information")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

