from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2OpError
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('api.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """
    Test class for the 'wait_for_db' command.
    """

    def test_wait_for_db_ready(self, patched_check):
        """
        Test case for when the database is immediately available.
        """

        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test case for when the database is not immediately available.
        """

        patched_check.side_effect = [Psycopg2OpError] * 2 + [OperationalError] * 2 + [True]
        call_command('wait_for_db')
        # Assert that the check was called six times before a successful connection
        self.assertEqual(patched_check.call_count, 5)
        patched_check.assert_called_with(databases=['default'])