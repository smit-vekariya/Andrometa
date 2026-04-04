from django.contrib import admin
from core.models import GoogleDriveAccount, File, Folder

# Register your models here.

@admin.register(GoogleDriveAccount)
class GoogleDriveAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'storage_summary', 'expiry', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('id', 'user__username', 'email')
    ordering = ('-created_at',)
    readonly_fields = (
        'storage_summary',
        'total_storage_display',
        'app_used_storage_display',
        'user_used_storage_display',
        'remaining_storage_display'
    )

    fieldsets = (
        (None, {
            'fields': ('user', 'email', 'expiry', 'is_active', 'priority')
        }),
        ('Tokens & Configuration', {
            'classes': ('collapse',),
            'fields': ('access_token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'root_folder_id')
        }),
        ('Storage Information', {
            'fields': (
                'storage_summary',
                'total_storage_display',
                'app_used_storage_display',
                'user_used_storage_display',
                'remaining_storage_display'
            )
        }),
    )

    def total_storage_display(self, obj):
        return obj._format_bytes(obj.total_storage)
    total_storage_display.short_description = "Total Drive Capacity"

    def app_used_storage_display(self, obj):
        return obj._format_bytes(obj.app_used_storage)
    app_used_storage_display.short_description = "Storage Used by App"

    def user_used_storage_display(self, obj):
        return obj._format_bytes(obj.user_used_storage)
    user_used_storage_display.short_description = "Storage Used (Other)"

    def remaining_storage_display(self, obj):
        return obj._format_bytes(obj.remaining_storage)
    remaining_storage_display.short_description = "Remaining Storage"

    def storage_summary(self, obj):
        total_used = obj.app_used_storage + obj.user_used_storage
        return f"{obj._format_bytes(total_used)} / {obj._format_bytes(obj.total_storage)}"
    storage_summary.short_description = "Storage (Used / Total)"

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
