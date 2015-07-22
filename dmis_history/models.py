from django.db import models
from django.utils import timezone


class History(models.Model):

    start_read_id = models.IntegerField(default=0)

    end_read_id = models.IntegerField(null=True)

    target = models.CharField(
        max_length=25,
        null=True)

    read_datetime = models.DateTimeField(
        default=timezone.now())

    read_model = models.CharField(
        max_length=25)

    comment = models.CharField(
        max_length=25,
        null=True)

    objects = models.Manager()

    def __str__(self):
        return '{}-{}'.format(self.start_read_id, self.end_read_id)

    class Meta:
        app_label = 'dmis_history'
        verbose_name_plural = 'History'
