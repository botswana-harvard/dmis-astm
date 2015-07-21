from django.db import models
from django.core.exceptions import ImproperlyConfigured, MultipleObjectsReturned

from .managers import AliquotManager


class Log(models.Model):

    last_id = models.IntegerField(default=0)

    class Meta:
        app_label = 'logger'


class BaseReadonlyModel(models.Model):

    do_not_migrate = True

#     def save(self, *args, **kwargs):
#         raise ImproperlyConfigured('Model {} is readonly (mssql)'.format(self))

    class Meta:
        abstract = True


class Receive(BaseReadonlyModel):

    receive_identifier = models.CharField(
        max_length=16,
        db_column='PID',
        unique=True
    )

    edc_specimen_identifier = models.CharField(
        max_length=25,
        db_column='edc_specimen_identifier')

    receive_datetime = models.DateTimeField(
        db_column='HEADERDATE')

    patient_identifier = models.CharField(
        max_length=25,
        db_column='PAT_ID')

    protocol_number = models.CharField(
        max_length=25,
        db_column='sample_protocolnumber')

    test_group = models.CharField(
        max_length=6,
        db_column='TID')

    drawn_datetime = models.DateTimeField(
        db_column='sample_date_drawn')

    site = models.CharField(
        max_length=25,
        db_column='sample_site_id')

    class Meta:
        db_table = 'LAB01Response'


class Aliquot(BaseReadonlyModel):

    receive = models.OneToOneField(
        to=Receive,
        to_field='receive_identifier',
        db_column='root',
    )

    aliquot_identifier = models.CharField(
        max_length=25,
        db_column='aliquot',
    )

    aliquot_datetime = models.DateTimeField(
        db_column='aliquot_datecreated')

    root_count = models.IntegerField(
        db_column='root_count',
    )

    aliquot_count = models.IntegerField(
        db_column='aliquot_count',
        null=True
    )

    objects = AliquotManager()

    class Meta:
        db_table = 'lab_aliquots'


class Result(BaseReadonlyModel):
    """Due to schema problems with DMIS, this model is both order and
    result of result/result_item."""

    receive = models.ForeignKey(
        to=Receive,
        to_field='receive_identifier',
        db_column='PID')

    result_uuid = models.CharField(
        max_length=36,
        db_column='Q001X0',
        unique=True,
    )

    result_datetime_char = models.CharField(
        max_length=25,
        db_column='HEADERDATE')

    result_guid = models.CharField(
        max_length=36,
        db_column='result_guid',
        null=True
    )

    tid = models.CharField(
        max_length=25,
        db_column='TID')

    @property
    def panel_name(self):
        if self.tid:
            return self.tid
        else:
            try:
                return self.receive.test_group
            except MultipleObjectsReturned:
                return 'ERROR'
        return None

    @property
    def order_datetime(self):
        return self.result_datetime

    @property
    def result_datetime(self):
        return self.result_datetime_char

    class Meta:
        db_table = 'LAB21Response'


class ResultItem(BaseReadonlyModel):

    result = models.ForeignKey(
        to=Result,
        to_field='result_uuid',
        db_column='QID1X0',
    )

    utestid_name = models.CharField(
        max_length=25,
        db_column='UTESTID',
        null=True)

    result_value = models.CharField(
        max_length=100,
        db_column='RESULT',
        null=True)

    result_quantifier = models.CharField(
        max_length=2,
        db_column='RESULT_QUANTIFIER',
        null=True)

    assay_datetime_char = models.CharField(
        max_length=25,
        db_column='sample_assay_date',
        null=True)

    instrument = models.CharField(
        max_length=2,
        db_column='MID',
        null=True)

    last_modified = models.CharField(
        max_length=25,
        db_column='KeyOpLastModified',
        null=True)

    status = models.CharField(
        max_length=15,
        db_column='STATUS',
        null=True)

    @property
    def assay_datetime(self):
        return self.assay_datetime_char

    @property
    def operator(self):
        return self.last_modified.replace('BHP\\', '')

    class Meta:
        db_table = 'LAB21ResponseQ001X0'


class Utestid(BaseReadonlyModel):

    test_group = models.CharField(
        max_length=10,
        db_column='TID',
        null=True)

    utestid_name = models.CharField(
        max_length=25,
        db_column='UTESTID',
        null=True)

    utestid_units = models.CharField(
        max_length=25,
        db_column='UTESTID_UNITS',
        null=True)

    utestid_longname = models.CharField(
        max_length=25,
        db_column='LONGNAME',
        null=True)

    class Meta:
        db_table = 'F0110Response'
