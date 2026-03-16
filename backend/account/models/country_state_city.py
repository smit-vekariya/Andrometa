from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=40, null=True, blank=True)
    code = models.CharField(max_length=5, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=40, null=True, blank=True)
    code = models.CharField(max_length=5, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    code = models.CharField(max_length=5, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name