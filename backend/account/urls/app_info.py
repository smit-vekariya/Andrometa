
from django.urls import path, include
from account.views.app_info import AppInfoView


urlpatterns = [
    path('app_info/', AppInfoView.as_view(), name="app_info"),
]