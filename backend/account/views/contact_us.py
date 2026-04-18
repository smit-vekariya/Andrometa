from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from account.serializers import ContactUsSerializer
from manager.manager import HttpsAppResponse

class ContactUsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = ContactUsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return HttpsAppResponse.send(data=[], status=1, message="Message sent successfully.")

            # Formatted error message for HttpsAppResponse
            errors = serializer.errors
            first_error_key = next(iter(errors))
            first_error_msg = errors[first_error_key][0]

            return HttpsAppResponse.send(data=[], status=0, message=str(first_error_msg))
        except Exception as e:
            return HttpsAppResponse.exception(str(e))
