from django.db import models
from django.core.exceptions import ImproperlyConfigured


class Receive(models.Model):

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

    def save(self, *args, **kwargs):
        raise ImproperlyConfigured('Model {} is readonly (mssql)'.format(self))

    class Meta:
        db_table = 'LAB01Response'


class Aliquot(models.Model):

    receive = models.ForeignKey(
        to=Receive,
        to_field='receive_identifier',
        db_column='root',
        unique=True
    )

    aliquot_identifier = models.CharField(
        max_length=25,
        db_column='aliquot',
    )

    aliquot_datetime = models.DateTimeField(
        db_column='aliquot_datecreated')

#     aliquot_root_id = models.CharField(
#         max_length=25,
#         db_column='root')

    root_count = models.IntegerField(
        max_length=25,
        db_column='root_count',
    )

    aliquot_count = models.IntegerField(
        db_column='aliquot_count',
        null=True
    )

    class Meta:
        db_table = 'lab_aliquots'


# class Order(models.Model):
# 
#     aliquot = models.ForeignKey(
#         to=Aliquot,
#         to_field='receive',
#         db_column='PID')
# 
# #     order_identifier = models.IntegerField(
# #         db_column='ID',
# #     )
# 
#     order_uuid = models.CharField(
#         max_length=36,
#         db_column='Q001X0',
#         unique=True,
#     )
# 
#     class Meta:
#         proxy = Result
#         db_table = 'LAB21Response'


class Result(models.Model):

    aliquot = models.ForeignKey(
        to=Aliquot,
        to_field='receive',
        db_column='PID')

    result_uuid = models.CharField(
        max_length=36,
        db_column='Q001X0',
        unique=True,
    )

    result_datetime = models.DateTimeField(
        db_column='HEADERDATE')

    result_guid = models.CharField(
        max_length=36,
        db_column='result_guid',
        null=True
    )

    class Meta:
        db_table = 'LAB21Response'


class ResultItem(models.Model):

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

    assay_datetime = models.DateTimeField(
        db_column='sample_assay_date',
        null=True)

    class Meta:
        db_table = 'LAB21ResponseQ001X0'
