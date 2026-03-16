from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

app_name = "app"

urlpatterns = [
    path('', Welcome.as_view(), name="welcome-page"),
    path('about_us/', AboutUs.as_view(), name="about-us-page"),
    path('contact_us/', ContactUs.as_view(), name="contact-us-page"),
    path('message/', MessageView.as_view(), name="message-page"),
]