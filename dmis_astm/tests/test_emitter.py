from astm import codec
from astm.compat import u
from astm.constants import ENCODING
from astm.constants import STX, ETX, ETB, CR, LF, CRLF
from django.test.testcases import TestCase
from django.utils import timezone
from getresults_astm.records import Header, CommonPatient, CommonOrder, CommonResult, Terminator
from history.models import History

from ..models import Receive, Result, ResultItem
from ..result_emitter import ResultEmitter


def decode_record(r):
    return codec.decode_record(r.encode(), ENCODING)


def f(s, e='latin-1'):
    return u(s).format(STX=u(STX),
                       ETX=u(ETX),
                       ETB=u(ETB),
                       CR=u(CR),
                       LF=u(LF),
                       CRLF=u(CRLF)).encode(e)


class TestEmitter(TestCase):

    def test_header_message(self):
        message = b'H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P|E 1394-97|20150108072227'
        values = codec.decode_record(f(message), ENCODING)
        header = Header(*values)
        self.assertEquals(message, codec.encode_record(header.to_astm(), ENCODING))

    def test_result_emitter_round_trip_with_order(self):
        receive = Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=timezone.now(),
            drawn_datetime=timezone.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        Result.objects.create(
            receive=receive,
            result_datetime_char=timezone.now().strftime('%Y%m%d%H%M%S'))
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        self.assertIsInstance(Header(*decode_record(message.decode())), Header)
        message = next(result_emitter)
        self.assertIsInstance(CommonPatient(*decode_record(message.decode())), CommonPatient)
        message = next(result_emitter)
        self.assertIsInstance(CommonOrder(*decode_record(message.decode())), CommonOrder)
        message = next(result_emitter)
        self.assertIsInstance(Terminator(*decode_record(message.decode())), Terminator)

    def test_result_emitter_round_trip_with_result(self):
        receive = Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=timezone.now(),
            drawn_datetime=timezone.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        result = Result.objects.create(
            receive=receive,
            result_datetime_char=timezone.now().strftime('%Y%m%d%H%M%S'),
            tid='PANEL'
        )
        ResultItem.objects.create(
            result=result,
            utestid_name='CD4',
            result_value='VALUE',
            result_quantifier='=',
            assay_datetime=timezone.now(),
            last_modified='BHP\\erik')
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        print(message)
        self.assertIsInstance(Header(*decode_record(message.decode())), Header)
        message = next(result_emitter)
        print(message)
        self.assertIsInstance(CommonPatient(*decode_record(message.decode())), CommonPatient)
        message = next(result_emitter)
        print(message)
        self.assertIsInstance(CommonOrder(*decode_record(message.decode())), CommonOrder)
        message = next(result_emitter)
        print(message)
        self.assertIsInstance(CommonResult(*decode_record(message.decode())), CommonResult)
        message = next(result_emitter)
        print(message)
        self.assertIsInstance(Terminator(*decode_record(message.decode())), Terminator)
        self.assertEqual(History.objects.all().count(), 1)

    def test_result_emitter_round_trip_with_patient(self):
        Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=timezone.now(),
            drawn_datetime=timezone.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        self.assertIsInstance(Header(*decode_record(message.decode())), Header)
        message = next(result_emitter)
        self.assertIsInstance(CommonPatient(*decode_record(message.decode())), CommonPatient)
        message = next(result_emitter)
        self.assertIsInstance(Terminator(*decode_record(message.decode())), Terminator)

    def test_result_emitter_round_trip_no_data(self):
        result_emitter = ResultEmitter(protocol_number=None)
        message = next(result_emitter)
        self.assertIsInstance(Header(*decode_record(message.decode())), Header)
        message = next(result_emitter)
        self.assertIsInstance(Terminator(*decode_record(message.decode())), Terminator)
