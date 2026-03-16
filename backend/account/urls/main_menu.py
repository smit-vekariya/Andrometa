
from django.urls import path, include
from account.views.main_menu import MainMenuView


urlpatterns = [
    path('main_menu/', MainMenuView.as_view(), name="main_menu"),
]