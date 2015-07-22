import unittest

from astm import constants
from astm.client import Client
from astm.tests.utils import DummyMixIn

from ..result_emitter import ResultEmitter


class DummyClient(DummyMixIn, Client):

    def __init__(self, *args, **kwargs):
        super(DummyClient, self).__init__(*args, **kwargs)
        self.timeout = None

    def create_socket(self, family, type):
        pass

    def connect(self, address):
        pass


class ClientTestCase(unittest.TestCase):

    def test_open_connection(self):
        emitter = ResultEmitter(protocol_number=None, target='edc')
        client = DummyClient(emitter.send)
        client.handle_connect()
        self.assertEqual(client.outbox[0], constants.ENQ)
