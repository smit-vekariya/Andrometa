from django.db import models
from account.models import BondUser


# Create your models here.
class ContactUs(models.Model):
    full_name = models.CharField(max_length =100)
    email = models.EmailField()
    mobile = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length =100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "Contact Us"
        ordering = ['-created_on']
