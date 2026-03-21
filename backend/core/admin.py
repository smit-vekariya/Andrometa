from django.contrib import admin
from core.models import GoogleDriveAccount, File, Folder

# Register your models here.

@admin.register(GoogleDriveAccount)
class GoogleDriveAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'expiry', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('id', 'user__username', 'email')
    ordering = ('-created_at',)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file_name', 'storage_account', 'folder', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('id', 'user__username', 'file_name')
    ordering = ('-created_at',)

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('id', 'user__username', 'name')
    ordering = ('-created_at',)
