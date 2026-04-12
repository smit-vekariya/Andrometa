from django.urls import path
from compressor.views.compressor_api import ImageCompressorView

app_name = "compressor"

urlpatterns = [
    path('compress/', ImageCompressorView.as_view(), name='compress'),
]
