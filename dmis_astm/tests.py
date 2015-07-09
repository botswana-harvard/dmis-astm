from astm import codec
from astm.constants import ENCODING

from dateutil import parser 
from datetime import datetime 
from django.test.testcases import SimpleTestCase
from getresults_astm.records import Header

from .dmis import Dmis
from .emitter import Emitter

from astm.compat import u
from astm.constants import STX, ETX, ETB, CR, LF, CRLF

def f(s, e='latin-1'):
    return u(s).format(STX=u(STX),
                       ETX=u(ETX),
                       ETB=u(ETB),
                       CR=u(CR),
                       LF=u(LF),
                       CRLF=u(CRLF)).encode(e)


class TestDmis(SimpleTestCase):

    def test_header_message(self):
        message = b'H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P|E 1394-97|20150108072227'
        values = codec.decode_record(f(message), ENCODING)
        header = Header(*values)
        self.assertEquals(message, codec.encode_record(header.to_astm(), ENCODING))

    def test_message_string(self):
        dmis = Dmis()
        for message in Emitter(dmis.new_messages()):
            self.assertIsInstance(message, bytes)
            self.assertTrue(message.decode()[0] in ['H', 'P', 'O', 'R'])

    def test_message_string_to_record(self):
        dmis = Dmis()
        for message in Emitter(dmis.new_messages()):
            values = codec.decode_record(message, ENCODING)
            self.assertIsInstance(Header(*values), Header)
