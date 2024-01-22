"""
Test custom Django management commands
"""

#We'll patch in order to mock behaviour of DB, we need to simulate when DB is returning a response
from unittest.mock import patch
#OperationalError is one of the possible erros that we might get when trying to connect to the DB before DB is ready
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command #Helper function provided by Django allowing us to call command by name, the one we testing
from django.db.utils import OperationalError #Another exception that may get thrown by the DB, depending on stage of startup process it is in
from django.test import SimpleTestCase #SimpleTestCase, because we testing whether DB ready or not, so no migrations to test DB is needed

@patch('core.management.commands.wait_for_db.Command.check')#This is the command we're going to be mocking
# Command.check - is provided by the BaseCommand class which allows us to check the status of the DB. We will be mocking the
# check method to simulate the repsonse. We can simulate the check method returning an exception or returning a value

#Because we add the @patch mentod to the class, it's going to add a new argument to all of the calls to our test methods so we catch
#it as a parameter - patched checked object or magic mock object that replaces check by patch will be passed in as an argument
# to the patched_check parameter then we can use the patched_check to customize the behaviour
class CommandTests(SimpleTestCase):
    """Test Commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for DB if DB ready"""
        patched_check.return_value = True #When check is called, just return value of True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default']) #ensures that the mock object (checked method inside our commad), is called with the parameters database=['default'] 

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for DB when getting OperationalError"""    
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True] #This is how we raise exceptions, by using a side_effect
        #The first time, we call the mocked object 2 times and we want it to raise the Psycopg2Error
        #The next 3 times, we wait an OperationalError
        #Often what happens, there's different stages of postgres starting. The first stage, postgress the application
        #hasn't even started so it's not ready to accept any connections which you then get the Psycopg2Error.
        #After that, the DB is ready to accept connections but it hasn't setup the testing (dev) DB that we want to use as yet
        #in which case Django throws an OperationalError from Djangos exception
        #After the 6th time, it will return a value of true. It knows that it is not an exception and instead should return the value instead

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])