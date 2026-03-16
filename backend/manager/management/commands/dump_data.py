from django.core.management import BaseCommand
from django.db import transaction, connections
from django.contrib.contenttypes.models import ContentType
from account.models import BondUser
from django.conf import  settings
import traceback, json, requests

# add this line in json if fk avaliable
# "fk": [{"field":"content_type", "fk_field":"model", "app_label": "contenttypes", "model": "contenttype"}],

class Command(BaseCommand):
    # python manage.py dump_data all
    command_name = "python manage.py dump_data {file_name}"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the file for dumping data")


    def handle(self, *args, **kwargs):
        try:
            self.is_dump_data = {}
            file_name = kwargs.get("name", False)

            with transaction.atomic():

                if file_name == "all":
                    with open(f"{settings.BASE_DIR}\\manager\\json_files\\{file_name}.json", "r") as file:
                        all_file_name = json.load(file)
                        all_file_name = all_file_name["all_file_name"]
                else:
                    all_file_name = [file_name]

                for name in all_file_name:
                    self.is_dump_data[name] = False
                    self.insert_data(name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))

    def insert_data(self, name):
        try:
            with transaction.atomic():
                with open(f"{settings.BASE_DIR}\\manager\\json_files\\{name}.json","r") as file:
                    file_data = json.load(file)

                content_type  = ContentType.objects.get(app_label=file_data["app_label"], model=file_data["model"])
                insert_model = content_type.model_class()

                unique_fields = file_data["unique_fields"] if "unique_fields" in file_data else None
                all_fk_model = file_data["fk"] if "fk" in file_data else None
                fk_model_dict = {}

                if all_fk_model:
                    for fk_model_name in all_fk_model:
                        fk_model_content_type = ContentType.objects.get(app_label=fk_model_name["app_label"],model=fk_model_name["model"])
                        fk_model_dict[fk_model_name["field"]] = {"model":fk_model_content_type.model_class(),"fk_field":fk_model_name["fk_field"]}

                data_list = []
                file_data["data"] =  list({frozenset(d.items()): d for d in file_data["data"]}.values())

                for data in file_data["data"]:
                    if fk_model_dict:
                        for field_name, model in fk_model_dict.items():
                            filter_kwargs = {model["fk_field"]: data[field_name]}
                            data[field_name + "_id"] = model["model"].objects.filter(**filter_kwargs).values("id").first()["id"]
                            data.pop(field_name)
                            unique_fields = [f"{x}_id" if x == field_name else x for x in unique_fields] if unique_fields else None

                    data_list.append(data)

                self.bulk_create_new(insert_model, data_list, unique_fields, name, file_data["app_label"], file_data["model"])

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))

    def bulk_create_new(self, model, data_list, unique_fields, name, app_label, app_model):
        try:
            with transaction.atomic():
                user_instance = BondUser.objects.filter(is_active=True, is_superuser=True).first()
                if unique_fields:
                    # Extract unique field values from data_list
                    unique_values = {field: set(map(lambda d: d[field], data_list)) for field in unique_fields}

                    # Fetch existing records in a single query
                    filters = {f"{field}__in": list(unique_values[field]) for field in unique_fields}
                    existing_records = model.objects.filter(**filters).values_list(*unique_fields)

                    # Convert tuples of existing values into a set for fast lookup
                    existing_values = set(existing_records)

                    new_objects = [
                        model(**data) for data in data_list
                        if tuple(data[field] for field in unique_fields) not in existing_values
                    ]
                else :
                    new_objects = [model(**data) for data in data_list]

                model.objects.bulk_create(new_objects, batch_size=100) if new_objects else []

                self.is_dump_data[name] = True
                self.stdout.write(self.style.SUCCESS(
                    f"SUCCESS: Data created successfully for '{name}': '{app_label}_{app_model}'"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))