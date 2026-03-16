from django.contrib import admin
from postoffice.models import EmailLog
# Register your models here.


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("subject","status","created_at","updated_at",)



