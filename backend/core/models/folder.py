from django.db import models
from manager.base_model import BaseModel

class Folder(BaseModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
                     'self', null=True, blank=True,
                     on_delete=models.CASCADE, related_name='sub_folders'
                 )

    class Meta:
        unique_together = ('user', 'parent', 'name')


    def __str__(self):
        return self.name
