from django.db import models
from datetime import datetime


class AppInfo(models.Model):
    device = models.CharField(max_length=200, unique=True)
    version = models.CharField(max_length=200, null=True, blank=True)
    url = models.CharField(max_length=200, null=True, blank=True)
    total_download = models.IntegerField(default=0, null=True, blank=True)
    force_update = models.BooleanField(default=False)

    def __str__(self):
        return self.device


class AppReport(models.Model):
    device_name = models.ForeignKey(AppInfo, on_delete=models.CASCADE, null=True, blank=True)
    device_id = models.CharField(max_length=200, null=True, blank=True, unique=True)
    first_login_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    last_login_date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    def __str__(self):
        return str(self.device_id)
