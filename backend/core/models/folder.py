from django.db import models
from account.models import BondUser
from manager.base_model import BaseModel

class Folder(BaseModel):
    user = models.ForeignKey(BondUser, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
                     'self', null=True, blank=True,
                     on_delete=models.CASCADE, related_name='subfolders'
                 )

    class Meta:
        unique_together = ('user', 'parent', 'name')

    def get_full_path(self):
        # Returns '/Projects/Design/'
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(parts)) + '/'

    def __str__(self):
        return self.get_full_path()
