import json
import requests
from django.conf import settings
import logging
import random
from manager.manager import HttpsAppResponse,create_from_exception,create_from_text
from django.db import transaction
from postoffice.models import EmailLog
from rest_framework.views import APIView
from django.utils import timezone
from postoffice.serializers import EmailLogSerializer
from django.core.mail import EmailMessage
from celery import shared_task


# for multiple receiver, cc, bcc add comma sepreter
# is_send, msg = SendMail.send_mail(request.user, True, "smit.intellial@gmail.com","this is subject","this is body","smit.intellial@gmail.com","smit.intellial@gmail.com")

class SendMail(APIView):
    def post(self, request):
        try:
            mail = request.data["mail_data"]
            is_send, msg =  self.send_mail(request.user, mail["is_now"], mail["to"], mail["subject"], mail["body"], mail["cc"], mail["bcc"])
            status_code = 1 if is_send else 0
            return HttpsAppResponse.send([], status_code, msg)
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    @staticmethod
    def send_mail(action_by, is_now, receiver, subject, message, cc=None, bcc=None):
        try:
            with transaction.atomic():
                sender = settings.EMAIL_HOST_USER
                action_by_id = action_by.id if action_by else None
                serializer = EmailLogSerializer(data={'mail_from': sender, 'mail_to': receiver, 'subject': subject, 'message': message, 'mail_cc': cc, 'mail_bcc': bcc, 'status':'pending', 'action_by_id':action_by_id, 'is_now':is_now})
                if serializer.is_valid():
                    instance = serializer.save()
                    if is_now:
                        is_send, msg = SendMail.send_mail_now(instance.id)
                        return is_send, msg
                    else:
                        send_mail_schedule.delay_on_commit(instance.id)
                        return True, "Your email is being processed and will be sent shortly."
                else:
                    raise Exception(str(serializer.errors))
        except Exception as e:
            create_from_exception(e)
            logging.exception("Something went wrong.")
            return False, str(e)

    @staticmethod
    def send_mail_now(mail_id):
        mail = EmailLog.objects.get(id=mail_id)
        try:
            sender = mail.mail_from
            receiver = [email.strip() for email in mail.mail_to.split(',')]
            subject = mail.subject
            message = mail.message
            cc = [email.strip() for email in mail.mail_cc.split(',')] if mail.mail_cc else []
            bcc = [email.strip() for email in mail.mail_bcc.split(',')] if mail.mail_bcc else []

            email = EmailMessage(subject, message, sender, receiver, bcc, cc=cc)
            email.send(fail_silently=True)

            mail.status = 'sent'
            mail.updated_at = timezone.now()
            mail.save()
            return True, "Mail send successfully."
        except Exception as e:
            mail.status = 'failed'
            mail.updated_at = timezone.now()
            mail.error_message = str(e)
            mail.save()

            create_from_exception(e)
            return False, str(e)


@shared_task
def send_mail_schedule(id):
    SendMail.send_mail_now(id)


#Mobile number is fix (contact green api for more: https://greenapi.com/en/docs/api)
def send_whatsapp_message(message):
    try:
        url=settings.GREEN_API
        payload={
                    "chatId": "9537127284@c.us",
                    "message": message,
                }
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        print(response.text.encode('utf8'))
    except Exception  as e:
      return HttpsAppResponse.exception(str(e))


def send_otp_to_mobile(mobile_no):
    try:
        if mobile_no:
            otp = random.randint(100000, 999999)
            url = settings.FAST2SMS
            api_key =  settings.FAST2SMS_API_KEY
            querystring = {"authorization":api_key,"variables_values":str(otp),"route":"otp","numbers":mobile_no}
            headers = { 'cache-control': "no-cache" }
            response = requests.request("GET", url, headers=headers, params=querystring)
            response = json.loads(response.text)
            if response["return"]:
                return otp
            else:
                create_from_text("Error in OTP sending", "Important", 10, f"response => {response}, info => mobile: '{mobile_no}' otp: '{otp}'")
                if response["status_code"] == 995:
                    return "Sending multiple sms to same number is not allowed. Please try again later."
                else:
                    return "We encountered an issue while sending the OTP. Please try again later."
        else:
            return "We encountered an issue while sending the OTP. Please try again later."
    except Exception as e:
        logging.exception("Something went wrong.")
        create_from_exception(e)
        return 0

