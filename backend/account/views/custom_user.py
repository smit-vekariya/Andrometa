from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import logging
from rest_framework.views import APIView, View
from account.serializers import CustomUserSerializers, CustomUserListSerializers
from account.models import CustomUser
from django.contrib.auth import authenticate
from django.core.cache import cache
from account.backends import AdminLoginBackend, AppLoginBackend
from manager import manager
from manager.manager import HttpsAppResponse
from django.shortcuts import render
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.models import update_last_login
from account.models import MainMenu,UserToken
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
from manager.models import GroupPermission
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from manager.manager import create_from_exception
from django.shortcuts  import redirect
from django.contrib.auth import login, authenticate, logout
from postoffice.views import SendMail
import textwrap
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.db.models import F
from postoffice.views import send_otp_to_email
from account.models import AuthOTP
from django.utils import timezone
import json



# Create your views here.

class UserProfile(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            user_id = request.user.id
            user_data = CustomUserListSerializers(CustomUser.objects.filter(id=user_id), many=True,  context={'request': request}).data
            return HttpsAppResponse.send([user_data], 1, "User Profile data get successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    def put(self, request, pk=None):
        try:
            data = request.data
            if request.FILES.get('file'):
                data["profile"] = request.FILES.get('file')

            serializer = CustomUserListSerializers(CustomUser.objects.get(pk=pk), data=data)
            if serializer.is_valid():
                serializer.save()
                return HttpsAppResponse.send([], 1, "User Profile Updated.")
            else:
                error_messages = ", ".join(value[0] for key, value in serializer.errors.items())
                return HttpsAppResponse.send([], 0, error_messages)
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        try:
            token = super().get_token(user)
            token['email'] = user.email
            access_token =  str(token.access_token)
            refresh_token = str(token)
            UserToken.objects.update_or_create(user_id=user.id,defaults={'access_token': access_token})
            update_last_login(None, user)
            response=[{"access":str(access_token),"refresh":refresh_token}]
            return response
        except Exception as e:
            logging.exception("Something went wrong.")
            manager.create_from_exception(e)

class AppLogin(APIView):
    authentication_classes =[]
    permission_classes = []

    def post(self,request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            if email and password:
                user = AppLoginBackend.authenticate(request, email=email, password=password)
                if user:
                    tokens = MyTokenObtainPairSerializer.get_token(user)
                    return HttpsAppResponse.send(tokens, 1, "Login successfully")
                else:
                    return HttpsAppResponse.send([], 0, "User is not found with this credential.")
            else:
                return HttpsAppResponse.send([], 0, "Email and password is require.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class AppRegistration(APIView):
    authentication_classes =[]
    permission_classes = []

    def post(self, request):
        try:
            serializer = CustomUserSerializers(data=request.data)
            if not serializer.is_valid():
                error_messages = ", ".join(
                    value[0] for key, value in serializer.errors.items()
                )
                return HttpsAppResponse.send([], 0, error_messages)

            otp = send_otp_to_email(request.data["email"])
            if len(str(otp)) > 6:
                return HttpsAppResponse.send([], 0, otp)

            AuthOTP.objects.update_or_create(
                key=f"register_{request.data['email']}",
                defaults={
                    "otp": otp,
                    "created_on": timezone.now(),
                    "value": json.dumps(request.data),
                }
            )
            return HttpsAppResponse.send([], 1, "OTP sent to email successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(e)


class VerifyAppRegistration(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            verify_data = request.data
            email = verify_data.get("email")
            otp   = verify_data.get("otp")

            if not email or not otp:
                return HttpsAppResponse.send([], 0, "Email and OTP are required.")

            user_data = AuthOTP.objects.filter(
                key=f"register_{email}",
            ).first()

            if not user_data:
                return HttpsAppResponse.send([], 0, "You need to register yourself first.")

            if str(user_data.otp) != str(otp):
                return HttpsAppResponse.send([], 0, "OTP verification failed. Please enter the correct OTP.")

            if user_data.expire_on < timezone.now():
                return HttpsAppResponse.send([], 0, "Your OTP has expired. Please request a new OTP.")

            data = json.loads(user_data.value)

            serializer = CustomUserSerializers(data=data)
            if not serializer.is_valid():
                error_messages = ", ".join(
                    value[0] for key, value in serializer.errors.items()
                )
                return HttpsAppResponse.send([], 0, error_messages)

            user = serializer.save()
            user_data.delete()

            tokens = MyTokenObtainPairSerializer.get_token(user)
            return HttpsAppResponse.send(tokens, 1, "Registration successful.")

        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class AppLogout(APIView):
    authentication_classes =[]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            logout(request)
            return HttpsAppResponse.send([], 1, "User logout successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class AdminLogin(APIView):
    authentication_classes =[]
    permission_classes = []

    def post(self,request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            if email and password:
                user = AdminLoginBackend.authenticate(request, email=email, password=password)
                if user:
                    tokens = MyTokenObtainPairSerializer.get_token(user)
                    return HttpsAppResponse.send(tokens, 1, "Login successfully")
                else:
                    return HttpsAppResponse.send([], 0, "User is not found with this credential.")
            else:
                return HttpsAppResponse.send([], 0, "Email and password is require.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class RegisterUser(APIView):
    authentication_classes =[]
    permission_classes = []
    def get(self, request):
        try:
            user_id = request.query_params.get("pk")
            user_instance = CustomUser.objects.get(id=user_id)
            user_data = CustomUserListSerializers(user_instance, context={'request': request}).data
            return HttpsAppResponse.send([user_data], 1, "data get successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    def post(self, request):
        try:
            user_id = self.request.query_params.get("id","")
            if user_id:
                serializer = CustomUserSerializers(instance=CustomUser.objects.get(id=user_id), data=request.data["registerForm"], partial=True)
            else:
                serializer = CustomUserSerializers(data=request.data["registerForm"])
            if serializer.is_valid():
                serializer.save()
                return HttpsAppResponse.send([], 1, "Registration successfully")
            else:
                error_messages = ", ".join(f"({key}) {value[0]}" for key, value in serializer.errors.items())
                return HttpsAppResponse.send([], 0, error_messages)
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    def delete(self, request):
        try:
            user_id = self.request.query_params.get("id","")
            CustomUser.objects.get(id=user_id).soft_delete()
            return HttpsAppResponse.send([], 1, "User deleted successfully")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

class ForgetPassword(ViewSet):
    authentication_classes = []
    permission_classes = []

    def send_mail(self, request, *args, **kwargs):
        try:
            email = request.data["email"]
            try:
                email_user =  CustomUser.objects.get(email=email, is_active=True, is_deleted=False)
            except ObjectDoesNotExist:
               return HttpsAppResponse.send([], 0, "This email is not registered or account is not active.")

            uid = urlsafe_base64_encode(force_bytes(email_user.id))
            token = default_token_generator.make_token(email_user)

            reset_link = f"{settings.FRONT_END_BASE_URL}/change_password/{uid}/{token}"

            subject = "Reset Your Password - PanelPrime"
            message =  textwrap.dedent(f'''
                Hi {email_user.full_name},

                We received a request to reset your password for your PanelPrime account.
                Please click the link below to reset your password:

                { reset_link }

                If you didn’t request this, you can safely ignore this email.

                Thanks,
                The PanelPrime Team
            ''')

            is_send, msg = SendMail.send_mail(None, True, email, subject, message)
            if not is_send:
                return HttpsAppResponse.send([], 0, msg)
            return HttpsAppResponse.send([], 1, "Check your email for the password reset link.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

    def change_password(self, request, *args, **kwargs):
        try:
            data = request.data
            uid = data.get("uid")
            token = data.get("token")
            password = data.get("password")

            uid = urlsafe_base64_decode(uid).decode()
            user = get_user_model().objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return HttpsAppResponse.send([], 1, "Password has been change successfully.")
            else:
                return HttpsAppResponse.send([], 0, "Invalid or expired token")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))
