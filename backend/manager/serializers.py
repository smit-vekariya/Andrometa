from rest_framework import serializers
from manager.models import SystemParameter
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, ClockedSchedule,SolarSchedule
from django_celery_results.models import TaskResult

class SystemParameterSerializers(serializers.ModelSerializer):
    class Meta:
        model = SystemParameter
        fields = '__all__'

    # def create(self, validate):
    #     SystemParameter.objects.create(*validate)


class IntervalScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabScheduleSerializer(serializers.ModelSerializer):
    crontab = serializers.CharField(source='__str__', read_only=True)
    crontab_human = serializers.SerializerMethodField()
    class Meta:
        model = CrontabSchedule
        fields = ['id','crontab','crontab_human']  
    
    def get_crontab_human(self, objects):
        return objects.human_readable
        


class ClockedScheduleSerializer(serializers.ModelSerializer):
    clock = serializers.CharField(source='__str__', read_only=True)
    class Meta:
        model = ClockedSchedule
        fields = ["id","clock"]

class SolarScheduleSerializer(serializers.ModelSerializer):
    solar = serializers.CharField(source="__str__", read_only=True) 
    class Meta:
        model = SolarSchedule
        fields = ["id","solar"]
        
class TaskResultSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = TaskResult
        fields = "__all__"

class PeriodicTaskSerializer(serializers.ModelSerializer):
    scheduler = serializers.SerializerMethodField()
    expires = serializers.SerializerMethodField()
    scheduler_type = serializers.SerializerMethodField()
    scheduler_id = serializers.SerializerMethodField()
    last_run_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    date_changed = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = PeriodicTask
        fields = ["id","name","task","enabled","expires","start_time","last_run_at","total_run_count","date_changed","scheduler","description","scheduler_type","scheduler_id","one_off","args","kwargs","expire_seconds"]

    def get_scheduler(self,objects):
        if objects.interval:
            return str(objects.interval)
        if objects.crontab:
            return str(objects.crontab.human_readable)
        if objects.clocked:
            return str(objects.clocked)
        
    def get_scheduler_id(self,objects):
        if objects.interval:
            return objects.interval.id
        if objects.crontab:
            return objects.crontab.id
        if objects.clocked:
            return objects.clocked.id
        
    def get_scheduler_type(self,objects):
        if objects.interval:
            return "interval"
        if objects.crontab:
            return "crontab"
        if objects.clocked:
            return "clocked"
        
    def get_expires(self,objects):
        if objects.expires:
            return str(objects.expires)
        elif objects.expire_seconds:
            return str(objects.expire_seconds) +" seconds"
        else:
            return None
        
class PeriodicTaskSaveSerializer(serializers.ModelSerializer):
    expires = serializers.DateTimeField(source='expire_date', format='%Y-%m-%d %H:%M:%S', required=False)   
    class Meta:
        model = PeriodicTask
        fields = '__all__'
        
    def validate(self, data):
        scheduler = [data["interval"], data["crontab"], data["clocked"]]
        if scheduler.count(None) != 2:
            raise serializers.ValidationError("Select one between  clocked, interval and crontab.")
        if data["clocked"] and data["one_off"] == False:
            raise serializers.ValidationError("One off must be true when clocked selected.")
        return data
        