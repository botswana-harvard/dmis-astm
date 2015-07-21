import os
import sys

from unipath import Path

from django.core.management.base import BaseCommand, CommandError

from getresults_astm.dispatchers import Dispatcher
from astm.server import Server


class Command(BaseCommand):
    help = 'Load data from a folder containing panels.csv, utestids.csv, panel_items.csv'

    def add_arguments(self, parser):
        parser.add_argument('host', nargs=1, type=str)
        parser.add_argument('port', nargs=1, type=str)

    def handle(self, *args, **options):
        host = str(options['host'][0]) or 'localhost'
        port = int(options['port'][0]) or 20581
        sys.stdout.write('Connecting to {} on port {} ...'.format(host, port))
        server = Server(host=host, port=port, dispatcher=Dispatcher)
        server.serve_forever()
