from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import FolderViewSet

router = DefaultRouter()
router.register('folders', FolderViewSet, basename='folder')

urlpatterns = [
    path('', include(router.urls)),
]