import sys

from astm import codec
from astm.constants import ENCODING

from getresults_astm.records import CommonPatient, Header, CommonOrder, CommonResult, Terminator
from getresults_astm.version import __version__ as getresults_version
from dmis_history import History

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
    def __init__(self, generator_type, protocol_number, target):
        if generator_type == 'records':
            self.messages = self.record_generator()
        else:
            self.messages = self.result_generator()
        self.protocol_number = protocol_number
        try:
            history = History.objects.filter(
                target=target, end_read_id__isnull=False
            ).order_by('-start_read_id')[0]
            self.last_read_id = history.end_read_id
        except IndexError:
            self.last_read_id = 0
        self.history = History.objects.create(
            read_model='{}.{}'.format(Receive._meta.app_label, Receive._meta.object_name),
            target=target,
            start_read_id=self.last_read_id,
            comment=protocol_number,
        )

    def __iter__(self):
        return self.messages

    def __next__(self):
        return next(self.messages)

    def astm_generator(self):
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
                self.history.end_read_id = self.last_read_id
                self.history.save()
            yield codec.encode_record(Terminator().to_astm(), ENCODING)
        except KeyboardInterrupt:
            yield codec.encode_record(Terminator().to_astm(), ENCODING)
            print('\nInterrupted. Stopping at last successful message. (receive.id={})\n'.format(
                self.last_read_id))
            self.history.save()

    def record_generator(self):
        """Yields a complete ordered message starting with H and ending with L."""
        print('\n\nPress CTRL-C to interrupt.\n')
        try:
            total = Receive.objects.filter(
                protocol_number=self.protocol_number, id__gte=self.last_read_id).count()
            n = 0
            for receive in Receive.objects.filter(
                    protocol_number=self.protocol_number, id__gte=self.last_read_id).order_by('id'):
                n += 1
                perc = round((100 * n / total))
                sys.stdout.write("Sending: {}% {}/{} (id={})   \r".format(perc, n, total, self.last_read_id))
                sys.stdout.flush()
                yield Header(**self.header_values())
                patient = Patient(receive)
                yield CommonPatient(**self.patient_values(patient, receive.receive_identifier))
                for result in Result.objects.filter(receive=receive):
                    order = Order(receive, result)
                    yield CommonOrder(**self.order_values(order))
                    for result_item in ResultItem.objects.filter(result=result):
                        yield CommonResult(**self.result_values(result_item))
                self.last_read_id = receive.id
                self.history.end_read_id = self.last_read_id
                self.history.save()
                yield Terminator()
        except KeyboardInterrupt:
            yield Terminator()
            print('Interrupted. Stopping at last successful message. (receive.id={})'.format(
                self.last_read_id))
            self.history.save()
        except Exception as err:
            print(str(err))

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
