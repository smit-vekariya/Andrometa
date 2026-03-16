from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest

class MobileNumberBackend(BaseBackend):
    def authenticate(self, request, mobile=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return None  # User with the provided mobile number does not exist
        return user

    def get_user(self, user_id):
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class AdminLoginBackend(BaseBackend):
    def authenticate(request, email=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return None
        except User.DoesNotExist:
            return None  # User with the provided mobile number does not exist
        return user

    def get_user(self, user_id):
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None