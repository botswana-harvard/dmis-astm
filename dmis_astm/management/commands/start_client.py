import os
import sys

from unipath import Path

from django.core.management.base import BaseCommand, CommandError

from astm.client import Client
from dmis_astm.result_emitter import ResultEmitter


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        emitter = ResultEmitter(type='records', protocol_number='BHP066', target='edc').record_generator
        host = str(args[0])
        port = int(args[1])
        sys.stdout.write('Connecting to {} on port {} ...\n'.format(host, port))
        client = Client(emitter=emitter, host=host, port=port)
        client.run(timeout=10)
        sys.stdout.write('Closed\n'.format(host, port))
