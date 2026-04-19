from django.urls import path
from compressor.views.compressor_api import ImageCompressorView, CheckAvailabilityView

app_name = "compressor"

urlpatterns = [
    path('compress/', ImageCompressorView.as_view(), name='compress'),
    path('availability/', CheckAvailabilityView.as_view(), name='availability'),
]
