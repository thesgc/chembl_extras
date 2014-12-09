__author__ = 'mnowotka'

from chembl_core_model.models import CompoundStructures
from django.core.management.base import BaseCommand
from optparse import make_option
from clint.textui import progress
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
import gzip

#------------------------------------------------------------------------------

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--chebi_id', default=True, dest='chebi_id',
            help='Include chebi_id.'),
        make_option('--chembl_id', default=True, dest='chembl_id',
            help='Include chembl_id.'),
        make_option('--downgraded', default=True, dest='downgraded',
            help='Include downgraded compounds.'),
        make_option('--out', dest='out_file',
            default='chembl.sdf.gz', help='Output file'),
        make_option('--database', dest='db',
            default=DEFAULT_DB_ALIAS, help='database')
        )
    help = ("Export all molecules from ChEMBL to one compressed *.sdf file.")
    args = '[--chebi_id, --chembl_id, --downgraded, --out]'

#------------------------------------------------------------------------------

    def handle(self, *args, **options):

        if settings.DEBUG:
            print "Django is in debug mode, which causes memory leak. Set settings.DEBUG to False and run again."
            return

        filename = options.get('out_file')
        chebi_id = options.get('chebi_id')
        chembl_id = options.get('chembl_id')
        downgraded = options.get('downgraded')
        db = options.get('db')
        verbosity = options.get('verbosity')

        if verbosity > 1:
            print self.help

        filters = {'molecule__chembl__entity_type':'COMPOUND'}

        if not downgraded:
            filters['molecule__downgraded'] = False

        fields = ['molfile']
        mol_template = '%s\n'

        if chembl_id:
            fields.append('molecule__chembl__chembl_id')
            mol_template += '> <chembl_id>\n%s\n\n'

        if chebi_id:
            fields.append('molecule__chebi_id')
            mol_template += '> <chebi_id>\n%s\n\n'

        mol_template += '$$$$\n'

        structures = CompoundStructures.objects.using(db).filter(**filters)
        n_structures = structures.count()

        if verbosity > 1:
            print "Found %s structures to export" % n_structures

        if not n_structures:
            print "Nothing to export..."

        else:
            f = gzip.open(filename, 'wb')
            try:
                for raw in progress.bar(structures.values_list(*fields).iterator(),
                            label="exporting... ", expected_size=n_structures):
                    f.write(mol_template % raw)

            finally:
                f.close()

        if verbosity > 1:
            print "Exporting done."

#------------------------------------------------------------------------------