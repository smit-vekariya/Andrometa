import datetime
import json
import logging
import math
import random
import pytz
import requests
import sys
import uuid
import traceback as traceback_mod
import warnings
from django.shortcuts import render
from dateutil import tz
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from django.utils.encoding import smart_str
from manager.models import ErrorBase, GroupPermission, SystemParameter
from account.models import BondUser
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

# you can customize exception handler response from this like serialize error respose and other error respose (https://www.django-rest-framework.org/api-guide/exceptions/)
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    create_from_exception(exception=exc, traceback=sys.exc_info()[2])
    logging.exception("Something went wrong.")

    # Custom handling for ValidationError
    if isinstance(exc, ValidationError):
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list) and value and hasattr(value[0], 'code'):
                    response.data[key] = value[0].title()

    if response is not None and "detail" in response.data:
        error = response.data["detail"]
        return HttpResponse(json.dumps({"data":[], "status": 0, "message": str(error)}))
        
    # return response
    return HttpResponse(json.dumps({"data":[], "status": 0, "message": str(exc)}))


def create_from_exception(self=None, url=None, exception=None, traceback=None, **kwargs):
    if not exception:
        exc_type, exc_value, traceback = sys.exc_info()
    elif not traceback:
        warnings.warn("Using just the ``exception`` argument is deprecated, send ``traceback`` in addition.", DeprecationWarning)
        exc_type, exc_value, traceback = sys.exc_info()
    else:
        exc_type = exception.__class__
        exc_value = exception

    def to_unicode(f):
        if isinstance(f, dict):
            nf = dict()
            for k, v in f.items():
                nf[str(k)] = to_unicode(v)
            f = nf
        elif isinstance(f, (list, tuple)):
            f = [to_unicode(f) for f in f]
        else:
            try:
                f = smart_str(f)
            except (UnicodeEncodeError, UnicodeDecodeError):
                f = "(Error decoding value)"
        return f

    tb_message = "\n".join(traceback_mod.format_exception(exc_type, exc_value, traceback))

    kwargs.setdefault("message", to_unicode(exc_value))
    level = logging.ERROR
    if kwargs.get("level"):
        level = kwargs["level"]

    ErrorBase.objects.create(class_name=exc_type.__name__, message=to_unicode(exc_value), traceback=tb_message, level=level)


def create_from_text(message, class_name=None, level=40, traceback=None):
    ErrorBase.objects.create(class_name=class_name, message=message, traceback=traceback, level=level)


def has_permission(user, act_code):
    if user.is_superuser:
        return True
    else:
        group_id = user.groups.id
        if Util.get_cache("public","perm" + str(group_id)) is None:
            group_perm = list(GroupPermission.objects.filter(group=group_id).values("permissions__act_name","permissions__act_code","has_perm"))
            Util.set_cache("public","perm" + str(group_id), group_perm, 604800)
        else:
            group_perm = Util.get_cache("public","perm" + str(group_id))
        
        for act in group_perm:
            if act["permissions__act_code"] == act_code:
                has_permission = act["has_perm"]
                return has_permission
    return False


def system_parameter(code):
    if Util.get_cache("public","sysparameter") is None:
        sys_para = list(SystemParameter.objects.values("code","value"))
        Util.set_cache("public","sysparameter", sys_para, 604800)
    else:
        sys_para = Util.get_cache("public","sysparameter")
    for para in sys_para:
        if para["code"] == code:
            return para["value"]
    raise Exception(f"'{code}' is avaliable in system parameter table.")


class HttpsAppResponse:
    def send(data,status,message):
        return HttpResponse(json.dumps({"data":data, "status": status, "message": message}))

    def exception(error):
        logging.exception("Something went wrong.")
        create_from_exception(error)
        return HttpResponse(json.dumps({"data":[], "status": 0, "message": str(error)}))


class Util(object):
    @staticmethod
    def create_unique_qr_code(batch_number):
        uuid_code = str(uuid.uuid4())
        uuid_upper = uuid_code.replace("-","")
        qr_code = f"QR-{batch_number}-{uuid_upper.upper()}"
        return qr_code

    @staticmethod
    def set_cache(schemas, key, value, time=3600):
        schemas_key = schemas + key
        cache.set(schemas_key, value, time)

    @staticmethod
    def get_cache(schemas, key):
        schemas_key = schemas + key
        if schemas_key in cache:
            return cache.get(schemas_key)
        return None

    @staticmethod
    def clear_cache(schemas, key):
        schemas_key = schemas + key
        if schemas_key in cache:
            cache.delete(schemas_key)
            
    @staticmethod
    def get_local_time(utctime, showtime=False, time_format=None):
        if utctime == "" or utctime is None or utctime == 0 or utctime == "-":
            return ""
        timezone_info = Util.get_timezone_info()
        from_zone = tz.gettz("UTC")
        to_zone = tz.gettz(timezone_info)
        utctime = utctime.replace(tzinfo=from_zone)
        new_time = utctime.astimezone(to_zone)
        if showtime:
            if time_format is None:
                time_format = "%d/%m/%Y %H:%M"
            return new_time.strftime(time_format)
        else:
            return new_time.strftime("%d/%m/%Y")
        
    @staticmethod
    def convert_time_to_utc(timeobj, time_format=None):
        local_timezone = Util.get_timezone_info()
        timezone = pytz.timezone(local_timezone)
        local_time = timezone.localize(timeobj)
        to_zone = tz.gettz("UTC")
        if time_format is None:
            time_format = "%d/%m/%Y %H:%M"
        utc_time = local_time.astimezone(to_zone).strftime(time_format)
        return utc_time

    @staticmethod
    def get_utc_datetime(local_datetime, has_time, timezone):
        naive_datetime = None
        local_time = pytz.timezone(timezone)

        if has_time:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y %H:%M")
        else:
            naive_datetime = datetime.datetime.strptime(local_datetime, "%d/%m/%Y")

        local_datetime = local_time.localize(naive_datetime, is_dst=None)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime
    
    @staticmethod
    def get_human_readable_time(minutes):
        time = ""
        cal_hrs = int(minutes / 60)
        days = int(cal_hrs / 24)
        hrs = cal_hrs - days * 24
        mins = int(minutes - (cal_hrs * 60))
        secs = int((minutes - mins - (hrs * 60) - (days * 24 * 60)) * 60)

        if days != 0:
            days = "%02d" % (days)
            time += str(days) + "d"
            if hrs != 0 or mins != 0 or secs != 0:
                time += ":"
        if hrs != 0:
            spent_hours = "%02d" % (hrs)
            time += str(spent_hours) + "h"
            if mins != 0 or secs != 0:
                time += ":"
        if mins != 0:
            mins = "%02d" % round(mins)
            time += str(mins) + "m"
            if secs != 0:
                time += ":"
        if secs != 0:
            secs = "%02d" % round(secs)
            time += str(secs) + "s"
        return time


def bad_request(request,exception):
    response = render(request,'manager/400.html')
    response.status_code = 400
    return response

def permission_denied(request, exception):
    response = render(request,'manager/403.html')
    response.status_code = 403
    return response

def page_not_found(request, exception):
    response = render(request,'manager/404.html')
    response.status_code = 404
    return response

def server_error_view(request):
    response = render(request,'manager/500.html')
    response.status_code = 500
    return response