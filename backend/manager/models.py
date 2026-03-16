from django.db import models
import logging
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from account.models import BondUser
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib import messages
from account.models import MainMenu

# Create your models here.
LOG_LEVELS = (
    (logging.INFO, _("info")),
    (logging.WARNING, _("warning")),
    (logging.DEBUG, _("debug")),
    (logging.ERROR, _("error")),
    (logging.FATAL, _("fatal")),
)

# Create your models here.
class ErrorBase(models.Model):
    class_name = models.CharField(_("type"), max_length=128, blank=True, null=True, db_index=True)
    level = models.PositiveIntegerField(choices=LOG_LEVELS, default=logging.ERROR, blank=True, db_index=True)
    message = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

# Temporary stop
# @receiver(post_save, sender=ErrorBase)
# def send_error_on_whatsapp(sender, instance, created, **kwargs):
#     from postoffice.views import send_whatsapp_message
#     if created:
#         messages = f"FROM: Panelprime BondClick\n{instance.created_on}\n --------------------------------------------\n{instance.class_name} : {instance.message}\n--------------------------------------------\n{instance.traceback}"
#         send_whatsapp_message(messages)


action_types =(
    ("insert", "Insert"),
    ("update", "Update"),
    ("delete", "Delete"),
    ("error", "Error")
)
class History(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id =  models.IntegerField(null=True, blank=True)
    action = models.TextField()
    action_type = models.CharField(max_length=100, choices=action_types, null=True, blank=True)
    ip_addr = models.CharField(default="", max_length=45)
    action_on = models.DateTimeField(auto_now=True)
    action_by = models.ForeignKey(BondUser, on_delete=models.PROTECT)


#with group create all group permission is created with all permission
@receiver(post_save, sender=Group)
def add_group_to_group_permission(sender, instance,created, **kwargs):
    if created:
        add_perm = [GroupPermission(group=instance, permissions=all_perm_instance) for all_perm_instance in AllPermissions.objects.all()]
        GroupPermission.objects.bulk_create(add_perm)



# set unique=True for act_code (remain)
class AllPermissions(models.Model):
    page_name = models.ForeignKey(MainMenu,on_delete=models.CASCADE)
    act_name = models.CharField(max_length=100)
    act_code = models.CharField(max_length=100)

    class Meta:
        unique_together = ('page_name', 'act_code')

    def __str__(self):
        return f"{self.page_name.name} - {self.act_name}"


#add this permission to all grop with has_perm false
@receiver(post_save, sender=AllPermissions)
def add_permission_to_grop_permission(sender, instance,created, **kwargs):
    if created:
        add_perm = [GroupPermission(group=group_instance, permissions=instance) for group_instance in Group.objects.all()]
        GroupPermission.objects.bulk_create(add_perm)


class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permissions = models.ForeignKey(AllPermissions, on_delete=models.CASCADE)
    has_perm = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'permissions')

    def save(self, *args, **kwargs):
        from manager.manager import Util
        Util.clear_cache("public","perm" + str(self.group.id))
        if self.pk is not None:
            #  You can not create group permission from here and update only 'has perm' field. if you want to update, delete that permission from all permission and create again."
            super().save(update_fields=['has_perm'])

    #for stop delete (code in admin.py)
    #You can not delete group permission from here. if you want to delete group permission you have to delete permission from all permission model.

class SystemParameter(models.Model):
    code = models.CharField(max_length=500)
    value = models.CharField(max_length=1000)
    description = models.TextField()

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        from manager.manager import Util
        Util.clear_cache("public","sysparameter")
        super().save(*args, **kwargs)