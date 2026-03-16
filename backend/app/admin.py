from django.contrib import admin
from app.models import ContactUs
# Register your models here.

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("full_name","mobile","email","subject", "resolved")
