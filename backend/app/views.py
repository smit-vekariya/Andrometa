from django.shortcuts import render
from rest_framework.views import APIView, View
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from manager.manager import HttpsAppResponse, Util
from app.serializers import *
from django.contrib import messages
from django.shortcuts  import redirect
from django.urls import reverse
from app.serializers import ContactUsSerializers
from rest_framework import viewsets
from rest_framework import filters
import json
from django.utils import timezone
from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from rest_framework.decorators import action
from manager.serializers import PeriodicTaskSerializer, TaskResultSerializer
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, ClockedSchedule
from app.forms import PeriodicTaskForm
from manager.decorators import query_debugger
from django_celery_results.models import TaskResult
from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class MessageView(APIView):
    authentication_classes =[]
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "app/message.html"

    def get(self, request, *args, **kwargs):
        return Response(status=200, template_name=self.template_name, data={"messages":request.GET.get("messages")})

class Welcome(APIView):
    authentication_classes =[]
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "app/welcome.html"

    def get(self, request, *args, **kwargs):
        return Response(status=200, template_name=self.template_name)

class AboutUs(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "app/about_us.html"

    def get(self, request, *args, **kwargs):
        return Response(status=200, template_name=self.template_name)


class ContactUs(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = ContactUsSerializers
    template_name = "app/contact_us.html"

    def get(self, request, *args, **kwargs):
        return Response(status=200, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return redirect(reverse('app:message-page') + '?messages=We recived your query. We will contact you soon.')
            else:
                return redirect(reverse('app:message-page') + '?messages=Something went wrong! Try later.')
        except Exception as e:
            return HttpsAppResponse.exception(str(e))
