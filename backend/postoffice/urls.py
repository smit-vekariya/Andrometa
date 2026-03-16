
from django.urls import path, include
from .views import *


app_name = "postoffice"

urlpatterns = [
    path('send_mail/', SendMail.as_view(), name='send_mail'),
]