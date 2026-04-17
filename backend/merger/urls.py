from django.urls import path
from merger.views import PDFMergerView

urlpatterns = [
    path('merge/', PDFMergerView.as_view(), name='pdf_merge'),
]
