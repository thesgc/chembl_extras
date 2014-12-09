__author__ = 'mnowotka'

from django.core.management.base import BaseCommand
from optparse import make_option
from clint.textui import progress
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem.AtomPairs import Pairs
from rdkit.Chem import MACCSkeys
from rdkit.Chem import rdMolDescriptors
from rdkit import rdBase

#------------------------------------------------------------------------------

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--in', dest='in_file',
            help='Input file'),
        make_option('--out', dest='out_file',
            default='out.fps.gz', help='Output file'),
        make_option('--fp_type', dest='fp_type',
            default='morgan', help='Type of fingerprint'),
        make_option('--n_bits', dest='n_bits',
            default=2048, help='Fingerprint length in bits'),
        make_option('--radius', dest='radius',
            default=2, help='Radius for the Morgan algorithm'),
        )
    help = ("Convert SDF to fps")
    args = '[--in, --out, --n_bits]'

#------------------------------------------------------------------------------

    def getFileHandle(self, path, mode):
        import os
        fileName, fileExtension = os.path.splitext(path)
        if fileExtension == '.gz':
            import gzip
            f = gzip.open(path, mode)
        elif fileExtension == '.bz2':
            import bz2
            f = bz2.BZ2File(path, mode)
        else:
            f = open(path, mode)
        return f

#------------------------------------------------------------------------------

    def handle(self, *args, **options):

        in_file = options.get('in_file')
        out_file = options.get('out_file')
        n_bits = options.get('n_bits')
        verbosity = options.get('verbosity')
        radius = options.get('radius')
        fp_type = options.get('fp_type')

        if verbosity > 1:
            print self.help

        inp = self.getFileHandle(in_file, 'rb')
        out = self.getFileHandle(out_file, 'wb')

        suppl = Chem.ForwardSDMolSupplier(inp)
        out.write("#FPS1\n#num_bits=%s\n#software=RDKit/%s\n" % (n_bits, rdBase.rdkitVersion))

        for i, mol in progress.mill(enumerate(suppl), expected_size=5):
            if mol:
                idx = i
                if mol.HasProp('chembl_id'):
                    idx = mol.GetProp('chembl_id')
                else:
                    try:
                        idx = Chem.InchiToInchiKey(Chem.MolToInchi(mol))
                    except:
                        pass
                if fp_type == 'morgan':
                    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol,radius,nBits=n_bits)
                elif fp_type == 'pair':
                    fp = Pairs.GetAtomPairFingerprintAsBitVect(mol)
                elif fp_type == 'maccs':
                    fp = MACCSkeys.GenMACCSKeys(mol)
                out.write("%s\t%s\n" % (DataStructs.BitVectToFPSText(fp), idx))

        if verbosity > 1:
            print "Conversion completed."

#------------------------------------------------------------------------------