from django.db import models
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from account.models import BondUser

# Create your models here.

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
)

class EmailLog(models.Model):
    mail_from = models.EmailField()
    mail_to = models.TextField()
    mail_cc = models.CharField(max_length=1000, null=True, blank=True) #cc mail limit 3
    mail_bcc = models.CharField(max_length=1000, null=True, blank=True) #bcc mail limit 3
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    is_now = models.BooleanField(default=True)
    action_by =models.ForeignKey(BondUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.subject

