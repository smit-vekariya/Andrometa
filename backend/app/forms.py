from django import forms
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, ClockedSchedule
from celery import current_app
from django.forms.widgets import Select
from celery.utils import cached_property
from django_celery_beat.admin import TaskSelectWidget,TaskChoiceField


class PeriodicTaskForm(forms.ModelForm):
    task = TaskChoiceField( label='Task (registered)',required=True)
    class Meta:
        model = PeriodicTask
        fields = '__all__'

   