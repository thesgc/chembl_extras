__author__ = 'mnowotka'

import os
from django.core.management.base import BaseCommand
from optparse import make_option
from django.db import DEFAULT_DB_ALIAS
from django.conf import settings
from django import db
from django.db import connections
from django.utils.datastructures import SortedDict
from django.core.management.commands.dumpdata import sort_dependencies

#-----------------------------------------------------------------------------------------------------------------------

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', dest='sourceDatabase', default=DEFAULT_DB_ALIAS, help='Source database'),
        make_option('--dumpfile', dest='dumpfile', default=None, help='Location of dump file.'),
        make_option('--datalimit', dest='dataLimit', default=10000, help='Data limit'),
        make_option('--app', dest='app', default='chembl_migration_model', help='App to be exported'),
        )
    help = ("Prepare configuration file for ora2pg tool.")
    args = '[appname appname.ModelName ...]'

    confTemplate = '''
ORACLE_HOME     %s
ORACLE_DSN      dbi:Oracle:host=%s;sid=%s;port=%s
ORACLE_USER     %s
ORACLE_PWD      %s
SCHEMA          %s
TABLES          %s
USER_GRANTS     1
DEBUG           0
EXPORT_SCHEMA   0
COMPILE_SCHEMA  0
TYPE            DATA
DATA_LIMIT      %s
CASE_SENSITIVE  0
OUTPUT          %s
DATA_TYPE	    DATE:date,LONG:text,LONG RAW:bytea,CLOB:text,NCLOB:text,BLOB:bytea,BFILE:bytea,RAW:bytea,ROWID:oid,FLOAT:double precision,DEC:decimal,DECIMAL:decimal,DOUBLE PRECISION:double precision,INT:integer,INTEGER:integer,REAL:real,SMALLINT:smallint,BINARY_FLOAT:double precision,BINARY_DOUBLE:double precision,TIMESTAMP:timestamp,TIMESTAMP WITH TIME ZONE:timestamp with time zone,TIMESTAMP WITH LOCAL TIME ZONE:timestamp
BZIP2   /bin/bzip2
GEN_USER_PWD    0
FKEY_DEFERRABLE 0
DEFER_FKEY      0
DROP_FKEY       0
DROP_INDEXES    0
PG_NUMERIC_TYPE 0
DEFAULT_NUMERIC NUMERIC
KEEP_PKEY_NAMES 1
DISABLE_TABLE_TRIGGERS 1
NOESCAPE        0
DISABLE_SEQUENCE        0
ORA_SENSITIVE   0
PLSQL_PGSQL     1
ORA_RESERVED_WORDS      audit,comment
FILE_PER_CONSTRAINT     0
FILE_PER_INDEX          0
FILE_PER_TABLE  0
TRANSACTION     serializable
PG_SUPPORTS_WHEN                1
PG_SUPPORTS_INSTEADOF   0
FILE_PER_FUNCTION       0
TRUNCATE_TABLE  0
FORCE_OWNER     0
STANDARD_CONFORMING_STRINGS     0
THREAD_COUNT            0
ALLOW_CODE_BREAK        1
XML_PRETTY      1
FDW_SERVER      orcl
ENABLE_MICROSECOND      0
DISABLE_COMMENT         1
    '''

#-----------------------------------------------------------------------------------------------------------------------

    def handle(self, *args, **options):
        from django.db.models import get_app

        #TODO : Check export mode
        db.reset_queries()
        sourceDatabase = options.get('sourceDatabase')
        dataLimit = options.get('dataLimit')
        app = get_app(options.get('app'))

        con = connections[sourceDatabase]
        if con.vendor != 'oracle':
            print "Source database has to be oracle."
            return

        user = settings.DATABASES[sourceDatabase]['USER']
        passwd = settings.DATABASES[sourceDatabase]['PASSWORD']
        host = settings.DATABASES[sourceDatabase]['HOST']
        port = settings.DATABASES[sourceDatabase]['PORT']
        name = settings.DATABASES[sourceDatabase]['NAME']

        app_list = SortedDict((app, None) for app in [app])
        tables = []
        sorted = sort_dependencies(app_list.items())
        lastObjectName = sorted[-1].__name__
        filename = lastObjectName + ".postgresql_psycopg2.sql"
        chemblSQLPath  = os.path.join(os.path.dirname(app.__file__),'sql', filename)
        location = chemblSQLPath
        oracleHome = os.environ['ORACLE_HOME']

        if options.get('dumpfile'):
            if not options.get('dumpfile').endswith('.sql'):
                location = os.path.join(options.get('dumpfile'), filename)
            else:
                location = options.get('dumpfile')


        for model in reversed(sorted):
            if not model._meta.managed:
                continue
            tables.append(model._meta.db_table)

        print self.confTemplate % (oracleHome, host, name, port, user, passwd, user, " ".join(tables), dataLimit, location)

        if location != chemblSQLPath:
            print "different! location = " + location + ", chemblSQLPath = " + chemblSQLPath
            f = open(location, 'w')
            f.close()
            os.symlink(location, chemblSQLPath)


#-----------------------------------------------------------------------------------------------------------------------