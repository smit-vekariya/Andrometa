from django.contrib import admin
from manager.models import ErrorBase, History, AllPermissions, GroupPermission, SystemParameter
from django.contrib import messages


# Register your models here.
@admin.register(ErrorBase)
class ErrorBaseAdmin(admin.ModelAdmin):
    list_display = ("class_name","level","message","traceback","created_on")

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'action', 'action_type', 'ip_addr', 'action_on', 'action_by')


@admin.register(AllPermissions)
class AllPermissionsAdmin(admin.ModelAdmin):
    list_display = ('page_name','act_name', 'act_code')

@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('group','permissions', 'has_perm')

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.WARNING, 'You can not create group permission from here and update only "has perm" field. if you want to update, delete that permission from all permission and create again.')
        super(GroupPermissionAdmin, self).save_model(request, obj, form, change)

    def delete_queryset(self, request, queryset):
        self.message_user(request, "You can not delete group permission from here. if you want to delete group permission you have to delete permission from all permission model.", level='warning')




@admin.register(SystemParameter)
class SystemParameterAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'description')