__author__ = 'mnowotka'

from chembl_core_model.models import CompoundMols
from chembl_core_model.models import CompoundStructures
from django.core.management.base import BaseCommand
from optparse import make_option
from clint.textui import progress
import gzip
from django import db
try:
    import cPickle as pickle
except ImportError:
    import pickle

#------------------------------------------------------------------------------

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--eps', default=0.3, dest='eps',
            help='Specifies the output serialization format for migration.'),
        make_option('--min_points', dest='min_points',
            default=100, help='Target database'),
        make_option('--out', dest='out_file',
            default='clusters.pkl.gz', help='Output file'),
        make_option('--in', dest='input',
            default=None, help='Input file'),
        )
    help = ("Cluster compounds in database.")
    args = '[--eps, --min_points, --out, --in]'

#------------------------------------------------------------------------------

    molecules = None
    infile = None
    filename = None
    UNCLASSIFIED = False
    NOISE = None

#------------------------------------------------------------------------------

    def _region_query(self, mol_id, eps):
        n_retries = 0
        while True:
            try:
                smiles = CompoundStructures.objects.only(
                                'canonical_smiles').get(pk=1).canonical_smiles

                if not smiles:
                    return []
                return [sim[0] for sim in
                        CompoundMols.objects.all().similar_to(
                            smiles, int((1.0 - eps) * 100)).values_list('pk')]
            except Exception as e:
                n_retries += 1
                db.close_connection()
                if n_retries >= 3:
                    self.save()
                    raise e
                pass

#------------------------------------------------------------------------------

    def _expand_cluster(self, pk, cluster_id, eps, min_points):
        seeds = self._region_query(pk, eps)
        if len(seeds) < min_points:
            self.molecules[pk] = self.NOISE
            return False
        else:
            self.molecules[pk] = cluster_id
            for seed in seeds:
                self.molecules[seed] = cluster_id

            while len(seeds):
                current_point = seeds[0]
                results = self._region_query(current_point, eps)
                n_results = len(results)
                if n_results >= min_points:
                    for result in results:
                        clas = self.molecules[result]
                        if clas == self.UNCLASSIFIED or clas == self.NOISE:
                            if clas == self.UNCLASSIFIED:
                                seeds.append(result)
                            self.molecules[result] = cluster_id
                seeds = seeds[1:]
            return True

#------------------------------------------------------------------------------

    def dbscan(self, eps, min_points):
        print "DBSCAN started..."
        cluster_id = 1
        for pk, cl in progress.bar(self.molecules.iteritems(),
                    label="clustering... ", expected_size=len(self.molecules)):
            if self.molecules[pk] == self.UNCLASSIFIED:
                if self._expand_cluster(pk, cluster_id, eps, min_points):
                    cluster_id += 1
        print "DBSCAN finished!"

#------------------------------------------------------------------------------

    def save(self):
        f = gzip.open(self.filename, 'wb')
        pickle.dump(self.molecules, f)
        f.close()

#------------------------------------------------------------------------------

    def load(self):
        f = gzip.open(self.filename, 'rb')
        self.molecules = pickle.load(f)
        f.close()

#------------------------------------------------------------------------------

    def handle(self, *args, **options):
        eps = options.get('eps')
        min_points = options.get('min_points')
        self.filename = options.get('out_file')
        self.infile = options.get('input')

        if not self.infile:
            print "prefetching data..."

            self.molecules = dict([(mol[0], self.UNCLASSIFIED) for mol in
                                    CompoundMols.objects.all().values_list('pk')])

            self.save()
            print "done"
        else:
            self.load()

        try:
            self.dbscan(eps, min_points)
        finally:
            self.save()

#------------------------------------------------------------------------------