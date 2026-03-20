from django.contrib import admin
from core.models import GoogleDriveAccount

# Register your models here.

@admin.register(GoogleDriveAccount)
class GoogleDriveAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'expiry', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('id', 'user__username', 'email')
    ordering = ('-created_at',)
