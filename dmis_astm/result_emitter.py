from astm import codec
from astm.constants import ENCODING

from getresults_astm.records import CommonPatient, Header, CommonOrder, CommonResult, Terminator
from getresults_astm.version import __version__ as getresults_version
from history import History

from .models import Result, ResultItem, Receive
from .version import __version__ as dmis_version


class Patient(object):

    def __init__(self, receive):
        self.patient_identifier = receive.patient_identifier
        self.dob = None
        self.registration_datetime = receive.receive_datetime
        self.gender = None


class Order(object):
    def __init__(self, receive, result):
        self.order_identifier = str(result.id)
        self.edc_specimen_identifier = receive.edc_specimen_identifier
        self.order_datetime = receive.receive_datetime
        self.sample_id = receive.receive_identifier
        self.panel_name = result.panel_name
        self.sampled_at = receive.receive_datetime
        self.created_at = result.result_datetime


class ResultEmitter(object):

    aliquot_identifiers = None

    """A generator to emit a result as a complete ASTM message."""
    def __init__(self, protocol_number):
        self.messages = self.result_generator()
        self.protocol_number = protocol_number
        try:
            self.last_read_id = History.objects.last().last_read_id
        except AttributeError:
            self.last_read_id = 0
        self.history = History.objects.create(read_model='{}.{}'.format(
            Receive._meta.app_label, Receive._meta.object_name))

    def __iter__(self):
        return self.messages

    def __next__(self):
        return next(self.messages)

    def result_generator(self):
        """Yields a complete ordered message starting with H and ending with L."""
        try:
            yield codec.encode_record(Header(**self.header_values()).to_astm(), ENCODING)
            for receive in Receive.objects.filter(
                    protocol_number=self.protocol_number, id__gte=self.last_read_id).order_by('id'):
                patient = Patient(receive)
                yield codec.encode_record(
                    CommonPatient(**self.patient_values(patient, receive.receive_identifier)).to_astm(), ENCODING)
                for result in Result.objects.filter(receive=receive):
                    order = Order(receive, result)
                    yield codec.encode_record(
                        CommonOrder(**self.order_values(order)).to_astm(), ENCODING)
                    for result_item in ResultItem.objects.filter(result=result):
                        yield codec.encode_record(
                            CommonResult(**self.result_values(result_item)).to_astm(), ENCODING)
                self.last_read_id = receive.id
                self.history.last_read_id = self.last_read_id
                self.history.save()
            yield codec.encode_record(Terminator().to_astm(), ENCODING)
        except KeyboardInterrupt:
            yield codec.encode_record(Terminator().to_astm(), ENCODING)
            print('Interrupted. Stopping at last successful message. (receive.id={})'.format(
                self.last_read_id))
            self.history.save()

    def send(self):
        return next(self.messages)

    def header_values(self):
        return dict(
            sender=['getresults-astm', getresults_version, 'dmis-astm', dmis_version],
            processing_id='P')

    def patient_values(self, patient, receive_identifier):
        return dict(
            birthdate=patient.dob,
            laboratory_id=receive_identifier,
            location='',
            name='',
            practice_id=patient.patient_identifier,
            sex=patient.gender,
            admission_date=patient.registration_datetime,
        )

    def order_values(self, order):
        return dict(
            biomaterial='',
            priority='R',
            sample_id=order.sample_id,
            test=order.panel_name,
            created_at=order.created_at,
            sampled_at=order.sampled_at,
            laboratory_field_1=order.order_identifier,
            laboratory_field_2=order.edc_specimen_identifier,
            action_code='X',  # order.action_code,
            report_type='F'  # order.report_type,
        )

    def result_values(self, result_item):
        return dict(
            abnormal_flag='',
            completed_at=result_item.result.result_datetime,
            instrument=result_item.instrument or 'UNK',
            operator=result_item.operator,
            status=result_item.status,
            test=['', '', '', result_item.utestid_name],
            value='{}{}'.format(result_item.result_quantifier or '', result_item.result_value),
        )
