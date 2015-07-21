from astm import codec
from astm.constants import ENCODING
from astm.compat import u
from astm.constants import STX, ETX, ETB, CR, LF, CRLF
from astm.codec import decode_record

from datetime import datetime
from django.test.testcases import SimpleTestCase
from django.utils import timezone

# from getresults.models import Order, Panel, Utestid, PanelItem, Result, ResultItem
# from getresults_aliquot.models import Aliquot, AliquotType
# from getresults_receive.models import Patient, Receive

from getresults_astm.records import Header, CommonPatient, CommonOrder, CommonResult, Terminator

from ..models import Receive, Result, Aliquot, ResultItem
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


class TestEmitter(SimpleTestCase):

    @property
    def receive(self):
        return Receive(
            patient_identifier='066-1234567-1',
            receive_datetime=timezone.now())

    @property
    def order(self):
        self.utestid = Utestid.objects.create(
            name='PHM', value_type='absolute', value_datatype='string')
        self.panel = Panel.objects.create(name='Viral Load')
        PanelItem.objects.create(panel=self.panel, utestid=self.utestid)
        return Order.objects.create(
            aliquot=self.aliquot,
            panel=self.panel,
            order_datetime=timezone.now(),
            action_code='X',
            report_type='F'
        )

    @property
    def aliquot_type(self):
        return AliquotType.objects.create(
            name='whole blood', alpha_code='WB', numeric_code='02')

    @property
    def aliquot(self):
        aliquot_type = self.aliquot_type
        receive = self.receive
        primary_aliquot = Aliquot.objects.create_primary(receive, aliquot_type.numeric_code)
        return Aliquot.objects.create(
            receive=receive,
            aliquot_identifier='{}{}{}'.format(
                receive.receive_identifier,
                primary_aliquot.own_segment,
                '{}{}'.format(aliquot_type.numeric_code, '02')),
            aliquot_type=aliquot_type,
            parent_aliquot_identifier=primary_aliquot.aliquot_identifier,
            primary_aliquot_identifier=primary_aliquot.aliquot_identifier,
        )

    def result(self, receive):
        return Result(
            receive=receive,
            analyzer_name='TAQMAN',
            operator='EW')

    def result_item(self, result, utestid):
        return ResultItem(
            result=result,
            value='750000',
            quantifier='<',
            result_datetime=timezone.now(),
            utestid=utestid,
            sender='148.1')

    def test_header_message(self):
        message = b'H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P|E 1394-97|20150108072227'
        values = codec.decode_record(f(message), ENCODING)
        header = Header(*values)
        self.assertEquals(message, codec.encode_record(header.to_astm(), ENCODING))

    def test_result_emitter_round_trip_with_order(self):
        receive = Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=datetime.now(),
            drawn_datetime=datetime.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        Result.objects.create(
            receive=receive,
            result_datetime=datetime.now())
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        print(message)
        Header(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonPatient(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonOrder(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        Terminator(*decode_record(message.decode()))

    def test_result_emitter_round_trip_with_result(self):
        receive = Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=datetime.now(),
            drawn_datetime=datetime.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        result = Result.objects.create(
            receive=receive,
            result_datetime=datetime.now())
        ResultItem.objects.create(
            result=result,
            utestid_name='CD4',
            result_value='VALUE',
            result_quantifier='=',
            assay_datetime=datetime.now())
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        print(message)
        Header(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonPatient(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonOrder(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonResult(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        Terminator(*decode_record(message.decode()))

    def test_result_emitter_round_trip_with_patient(self):
        Receive.objects.create(
            receive_identifier='SAMPLE_ID',
            receive_datetime=datetime.now(),
            drawn_datetime=datetime.now(),
            patient_identifier='PATIENT_ID',
            protocol_number='PROTOCOL_ID',
            edc_specimen_identifier='EDC_SPECIMEN_ID')
        result_emitter = ResultEmitter(protocol_number='PROTOCOL_ID')
        message = next(result_emitter)
        print(message)
        Header(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        CommonPatient(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        Terminator(*decode_record(message.decode()))

    def test_result_emitter_round_trip_no_data(self):
        result_emitter = ResultEmitter()
        message = next(result_emitter)
        print(message)
        Header(*decode_record(message.decode()))
        message = next(result_emitter)
        print(message)
        Terminator(*decode_record(message.decode()))
