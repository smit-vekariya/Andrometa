
import logging
from rest_framework.views import APIView
from account.serializers import CustomUserSerializers, CustomUserListSerializers, CustomUserProfileSerializers, AppForgotPasswordSerializer, AppVerifyForgotPasswordOTPSerializer, AppResetPasswordSerializer, AppGoogleLoginSerializer
from account.models import CustomUser
from account.backends import AdminLoginBackend, AppLoginBackend
from manager import manager
from manager.manager import HttpsAppResponse
from django.contrib.auth.models import update_last_login
from account.models import UserToken
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from postoffice.views import SendMail
import textwrap
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework.viewsets import ViewSet
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from postoffice.views import send_otp_to_email
from account.models import AuthOTP
from django.utils import timezone
import json
from manager.manager import custom_response_errors
from account.authentication import MyTokenObtainPairSerializer


# Create your views here.

class UserProfile(APIView):
    def get(self, request, pk=None):
        try:
            user_id = request.user.id
            user_data = CustomUserProfileSerializers(CustomUser.objects.filter(id=user_id), many=True,  context={'request': request}).data
            return HttpsAppResponse.send(user_data, 1, "User Profile data get successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


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
                    return HttpsAppResponse.send([{"access": tokens._cached_access_token_str, "refresh": str(tokens)}], 1, "Login successfully")
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
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            response, otp = send_otp_to_email(request.data["email"], purpose="registration")
            if not response:
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
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            user = serializer.save()
            user_data.delete()

            tokens = MyTokenObtainPairSerializer.get_token(user)
            return HttpsAppResponse.send([{"access": tokens._cached_access_token_str, "refresh": str(tokens)}], 1, "Registration successful.")

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


class AppForgotPassword(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = AppForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            email = serializer.validated_data["email"]
            response, otp = send_otp_to_email(email, purpose="forgot_password")
            if not response:
                return HttpsAppResponse.send([], 0, otp)

            AuthOTP.objects.update_or_create(
                key=f"forgot_{email}",
                defaults={
                    "otp": otp,
                    "created_on": timezone.now(),
                    "value": email,
                }
            )
            return HttpsAppResponse.send([], 1, "OTP sent to your email successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class AppVerifyForgotPasswordOTP(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = AppVerifyForgotPasswordOTPSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            email = serializer.validated_data["email"]
            otp_record = serializer.validated_data["otp_record"]

            otp_record.value = f"verified_{email}"
            otp_record.save()

            return HttpsAppResponse.send({"email": email}, 1, "OTP verified successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class AppResetPassword(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = AppResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            email = serializer.validated_data["email"]
            password   = serializer.validated_data["password"]
            otp_record = serializer.validated_data["otp_record"]

            user = CustomUser.objects.get(email=email, is_active=True)
            user.password = make_password(password)
            user.save()

            otp_record.delete()
            return HttpsAppResponse.send([], 1, "Password reset successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


class AppGoogleLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = AppGoogleLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpsAppResponse.send([], 0, custom_response_errors(serializer.errors))

            email = serializer.validated_data["email"]
            google_id = serializer.validated_data["google_id"]
            full_name = serializer.validated_data["full_name"]
            
            # Check if user exists
            user_qs = CustomUser.objects.filter(email=email)
            if user_qs.exists():
                user = user_qs.first()
                if user.auth_provider != "google":
                    return HttpsAppResponse.send([], 0, f"Email already registered using {user.auth_provider}. Please login using your existing method.")
                
                # Update google_id just in case it changed or wasn't set (though normally it should be set)
                if user.google_id != google_id:
                    user.google_id = google_id
                    user.save()
            else:
                # Create user
                user = CustomUser.objects.create(
                    email=email,
                    full_name=full_name,
                    google_id=google_id,
                    auth_provider="google",
                    is_app_user=True,
                    is_active=True
                )
            
            tokens = MyTokenObtainPairSerializer.get_token(user)
            return HttpsAppResponse.send([{"access": tokens._cached_access_token_str, "refresh": str(tokens)}], 1, "Login successful.")

        except Exception as e:
            return HttpsAppResponse.exception(str(e))