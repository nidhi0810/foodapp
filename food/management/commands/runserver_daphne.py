# your_app/management/commands/runserver_daphne.py

from django.core.management.base import BaseCommand
from daphne.server import Server
from mysite.asgi import application  # Import your ASGI application

class Command(BaseCommand):
    help = 'Runs the Django project with Daphne ASGI server.'

    def add_arguments(self, parser):
        parser.add_argument(
            'port',
            nargs='?',
            type=int,
            help='Port number to run Daphne on. Default is 8000.',
            default=8000
        )
        parser.add_argument(
            '--host',
            type=str,
            help='Host to run the server on. Default is 127.0.0.1.',
            default='127.0.0.1'
        )

    def handle(self, *args, **options):
        port = options['port']
        host = options['host']
        server = Server(application=application, endpoints=[f"tcp:port={port}:interface={host}"])
        server.run()
