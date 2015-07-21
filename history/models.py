from django.db import models
from django.utils import timezone


class History(models.Model):

    last_read_id = models.IntegerField(default=0)

    last_read_datetime = models.DateTimeField(
        default=timezone.now())

    read_model = models.CharField(
        max_length=25)

    objects = models.Manager()

    def __str__(self):
        return str(self.last_read_id)

    class Meta:
        app_label = 'history'
