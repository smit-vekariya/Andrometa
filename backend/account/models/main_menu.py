from django.db import models

class MainMenu(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, null=True,blank=True)
    sequence = models.CharField(max_length=100)
    url = models.CharField(max_length=100, null=True, blank=True)
    is_parent = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
