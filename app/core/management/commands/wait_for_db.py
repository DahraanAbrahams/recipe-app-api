"""
Django command to wait for DB to be available
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Entrypoint for command"""
        self.stdout.write('Waiting for database')
        db_up = False   #We assuming DB isn't up until we know that it is
        while db_up is False:
            try:
                self.check(databases=['default']) #If the DB isn't ready, it will throw an exception
                db_up = True    #If exceptions weren't raised, we know the DB is ready and the loop will stop
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1) #If exception is raised, python will wait 1 second before it continues with the loop

        self.stdout.write(self.style.SUCCESS('Database available!'))
'''
noqa
dahraanabrahams@Dahraans-MacBook-Air recipe-app-api % docker-compose run --rm app sh -c "python manage.py test"
[+] Running 1/0
 ✔ Container recipe-app-api-db-1  Created                                                    0.0s 
[+] Running 1/1
 ✔ Container recipe-app-api-db-1  Started                                                    0.4s 
System check identified no issues (0 silenced).
..Waiting for database
Database unavailable, waiting 1 second...
Database unavailable, waiting 1 second...
Database unavailable, waiting 1 second...
Database unavailable, waiting 1 second...
Database unavailable, waiting 1 second...
Database available!
.Waiting for database
Database available!
.
----------------------------------------------------------------------
Ran 4 tests in 0.008s
'''