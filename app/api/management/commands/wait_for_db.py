from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is ready."""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_ready = False
        while db_ready is False:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database is not ready, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is ready!'))
