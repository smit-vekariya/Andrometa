from django.urls import path
from .views import Home, Privacy, Terms, Contact, Features

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('features/', Features.as_view(), name='features'),
    path('privacy/', Privacy.as_view(), name='privacy'),
    path('terms/', Terms.as_view(), name='terms'),
    path('contact/', Contact.as_view(), name='contact'),
]