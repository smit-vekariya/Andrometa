
from django.contrib import admin
from django.urls import path
from core import views as core_views

urlpatterns = [
    path('oauth/callback', core_views.oauth_callback, name='oauth_callback'),
]
