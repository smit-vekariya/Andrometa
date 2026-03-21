from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import logging
from rest_framework.views import APIView, View
from account.serializers import CustomUserSerializers, CustomUserListSerializers
from account.models import CustomUser
from django.contrib.auth import authenticate
from django.core.cache import cache
from account.backends import AdminLoginBackend
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


class MainMenuView(APIView):

    def get(self, request):
        try:
            if request.user.is_superuser is False:
                can_view_page = GroupPermission.objects.select_related('permissions').filter(group=request.user.groups.id,has_perm=True,permissions__act_code='can_view').values_list("permissions__page_name_id", flat=True)
                menu = list(MainMenu.objects.filter(id__in=can_view_page).values().order_by("sequence"))
            else:
                menu = list(MainMenu.objects.values().order_by("sequence"))
            return HttpsAppResponse.send(menu, 1, "Get Main Menu data successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


