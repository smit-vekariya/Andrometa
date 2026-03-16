from django_celery_beat.models import *
from manager.manager import HttpsAppResponse
import json
from celery import current_app
from rest_framework import viewsets, generics
from celery import shared_task
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from manager.manager import create_from_exception
from manager.serializers import *
from django_celery_results.models import TaskResult

# https://django-celery-beat.readthedocs.io/en/latest/

class CreateScheduler(viewsets.ViewSet):
    permission_classes =[]
    authentication_classes =[]

    def create_scheduler(self, request):
        try:
            data = request.POST
            schedule_type =data["type"]
            interval,crontab,clocked= None, None, None
            if schedule_type == "interval" :
                interval = self.create_interval_scheduler(request,data)
            elif schedule_type == "crontab" :
                crontab = self.create_crontab_scheduler(request,data)
            elif schedule_type == "clocked" :
                clocked = self.create_clocked_scheduler(request,data)
            else:
                return HttpsAppResponse.send([], 0, "Invalid schedule type.")

            if interval or crontab or clocked:
                PeriodicTask.objects.create(
                    interval=interval,
                    crontab=crontab,
                    clocked=clocked,
                    name=data["name"],
                    task=data["task"], # dropdown
                    args=json.dumps(json.loads(data["args"])),
                    one_off=True if schedule_type == "clocked" else False
                    # expire_seconds =10,
                    # kwargs=json.dumps({
                    #     'be_careful': True,
                    # }),
                    # expires=datetime.strptime(data["expires"], '%Y-%m-%d %H:%M:%S.%f') if data["expires"] else None
                    # expires= datetime.now()  + timedelta(seconds=60)
                )
                return HttpsAppResponse.send([], 1, "Periodic task created successfully.")
            else:
                return HttpsAppResponse.send([], 0, f"Something wrong with {schedule_type} scheduler.")
        except  Exception as e:
            return HttpsAppResponse.exception(str(e))

    def create_interval_scheduler(self, request, data):
        try:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=data["every"],
                period=data["period"] #dropdown
            )
            return schedule
        except Exception as e:
            create_from_exception(e)
            return None

    def create_crontab_scheduler(self, request, data):
        try:
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=data["minute"],
                hour=data["hour"],
                day_of_week=data["day_of_week"], #0 for Sunday
                day_of_month=data["day_of_month"],
                month_of_year=data["month_of_year"],
            )
            return schedule
        except Exception as e:
            create_from_exception(e)
            return None

    def create_clocked_scheduler(self, request, data):
        try:
            schedule, created = ClockedSchedule.objects.get_or_create(
                clocked_time=data["clocked_time"],
            )
            return schedule
        except Exception as e:
            create_from_exception(e)
            return None


class PeriodicTaskView(viewsets.ModelViewSet):
    queryset = PeriodicTask.objects.all().select_related('interval','crontab','clocked')
    serializer_class = PeriodicTaskSerializer

    def list(self, request, *args, **kwargs):
        periodic_id = self.request.query_params.get("id")
        queryset = self.get_queryset()
        if periodic_id:
            serializer = self.get_serializer(instance=queryset.get(id=periodic_id))
        else:
            serializer = self.get_serializer(queryset, many=True)
        return HttpsAppResponse.send(serializer.data, 1, "Periodic task listed successfully.")

    def periodic_task_result(self, request, *args, **kwargs):
        periodic_name = self.request.query_params.get('periodic_name')
        results = TaskResult.objects.filter(periodic_task_name=periodic_name)
        if results:
            serializer = TaskResultSerializer(results, many=True)
            return HttpsAppResponse.send(serializer.data, 1, "Periodic task result listed successfully.")
        return HttpsAppResponse.send([], 0, "Periodic task result not found.")

    def create_update(self, request, *args, **kwargs):
        try:
            periodic_id = self.request.query_params.get("periodic_id")
            serializers = PeriodicTaskSaveSerializer(self.get_queryset().get(id=periodic_id), data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return HttpsAppResponse.send([], 1, "Update task successfully")
            else:
                return HttpsAppResponse.send([], 0, serializers.errors["non_field_errors"][0].title())
        except Exception as e:
            return HttpsAppResponse.exception(str(e))


@shared_task(name="test", bind=True)
def test(self):
    print("=====> this is for testing <========")


class TaskPreData(generics.ListAPIView):
    permission_classes =[]
    authentication_classes =[]
    celery_app = current_app
    serializer_class = CrontabScheduleSerializer # add this line becuase of swagger error

    def get(self, request, *args, **kwargs):
        try:
            tasks = sorted(name for name in self.celery_app.tasks if not name.startswith('celery.'))
            interval = list(IntervalSchedule.objects.annotate(name=Concat(Value("every "), F("every"),Value(" "), F("period"), output_field=CharField())).values("id","name"))
            crontab = CrontabScheduleSerializer(CrontabSchedule.objects.all(), many=True).data
            clocked = ClockedScheduleSerializer(ClockedSchedule.objects.all(), many=True).data
            solar = SolarScheduleSerializer(SolarSchedule.objects.all(), many=True).data
            return HttpsAppResponse.send([{"register_task":tasks,"interval":interval,"crontab":crontab,"solar":solar,"clocked":clocked}], 1, "Pre data get successfully.")
        except Exception as e:
            return HttpsAppResponse.exception(str(e))

