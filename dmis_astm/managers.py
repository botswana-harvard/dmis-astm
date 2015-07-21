from django.apps import apps
from django.db import models


class AliquotManager(models.Manager):

    def orders(self, aliquot_identifier):
        Result = apps.get_model('dmis_astm', 'Result')
        return Result.objects.filter(aliquot__aliquot_identifier=aliquot_identifier)
