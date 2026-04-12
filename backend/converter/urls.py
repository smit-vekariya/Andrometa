from django.urls import path
from converter.views.converter_api import FileConverterView

app_name = "converter"

urlpatterns = [
    path('convert/', FileConverterView.as_view(), name='convert'),
]
