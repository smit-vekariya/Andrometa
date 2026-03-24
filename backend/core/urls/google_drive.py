
from django.contrib import admin
from django.urls import path
from core.views import google_drive as google_drive_views

urlpatterns = [
    path('oauth/callback', google_drive_views.oauth_callback, name='oauth_callback'),
    path("google/auth-url/", google_drive_views.google_auth_url),
    path("google/callback/", google_drive_views.google_callback),
    path("google/accounts/", google_drive_views.GoogleDriveAccountViewSet.as_view({'get': 'list'}), name="google-accounts-list-create"),
    path("google/accounts/<int:pk>/", google_drive_views.GoogleDriveAccountViewSet.as_view({'get': 'retrieve'}), name="google-accounts-detail"),
]
