from astm import codec
from astm.constants import ENCODING
from astm.client import Client

from getresults_astm.records import CommonPatient, Header, CommonOrder, CommonResult, Terminator


class Emitter(object):

    def __init__(self, messages):
        self.messages = messages

    def __iter__(self):
        for message in self.messages:
            rectype = message.get('type')
            values = message.get('values')
            if rectype == 'H':
                yield codec.encode_record(Header(**values).to_astm(), ENCODING)
            elif rectype == 'P':
                yield codec.encode_record(CommonPatient(**values).to_astm(), ENCODING)
            elif rectype == 'O':
                yield codec.encode_record(CommonOrder(**values).to_astm(), ENCODING)
            elif rectype == 'R':
                yield codec.encode_record(CommonResult(**values).to_astm(), ENCODING)
            elif rectype == 'L':
                yield codec.encode_record(Terminator(**values).to_astm(), ENCODING)
            else:
                yield message

    def __next__(self):
        return self
