from django.urls import path
from .views import Home, Privacy, Terms, Contact

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('privacy/', Privacy.as_view(), name='privacy'),
    path('terms/', Terms.as_view(), name='terms'),
    path('contact/', Contact.as_view(), name='contact'),
]