from django.urls import path
from account.views.contact_us import ContactUsView

urlpatterns = [
    path('contact_us/', ContactUsView.as_view(), name='contact-us'),
]
