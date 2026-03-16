from django.core.management.base import BaseCommand
import pandas as pd
from account.models import City, State
from backend import settings
from manager import manager
from django.db import transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                df = pd.read_excel(str(settings.BASE_DIR) +'/manager/files/Districts.xlsx')
                for index, row in df.iterrows():
                    data,response = State.objects.get_or_create(name=row['State'])
                    City.objects.get_or_create(name=row['City'],state_id=data.id)
                print("City and state add successfully.")
        except Exception as e:
            manager.create_from_exception(e)
            print("Something went wrong.")