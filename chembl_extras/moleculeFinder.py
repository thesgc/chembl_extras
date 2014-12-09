__author__ = 'mnowotka'

import gzip
from Bio import trie
from Bio import triefind
from chembl_business_model import utils
from chembl_business_model.models import CompoundStructures

class MoleculeFinder():

#-----------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        triefind.DEFAULT_BOUNDARY_CHARS = triefind.DEFAULT_BOUNDARY_CHARS.translate(None, utils.INCHI_SPECIAL_CHARS)

        self.index = trie.trie()

        for inchi in CompoundStructures.objects.all().values_list('standard_inchi', 'molecule_id'):
            for chunk in inchi[0].split('/')[1:]:
                if len(chunk) > 2:
                    if self.index.get(str(chunk)):
                        self.index[str(chunk)].append(inchi[1])
                    else:
                        self.index[str(chunk)] = [inchi[1]]

#-----------------------------------------------------------------------------------------------------------------------

    def find(self, string):
        if len(string) < 3:
            return []

        if 'InChI=1S'.find(string) != (-1) and len(string) > 3:
            return CompoundStructures.objects.all()

        if string[1:-1].find('/') == (-1):
            if string.find('*') == (-1):
                if string.endswith('/'):
                    return self.index.get(str(string.translate(None, '/')))
                else:
                    res = triefind.find(string, self.index)
                    lengths = map(lambda x: x[2] - x[1], res)
                    if not lengths:
                        return []
                    maxlen = max(lengths)
                    indices = [i for i, x in enumerate(lengths) if x == maxlen]
                    return sum(map(lambda x: self.index[str(x[0])], [i for j, i in enumerate(res) if j in indices]), [])
            else:
                return  sum(
                    map(lambda x: x[1], self.index.get_approximate(string.translate(None, '/'), string.count('*'))), [])

        else:
            res = triefind.find(string, self.index)
            keys = map(lambda x: x[0], res)
            score = dict()
            for key in keys:
                for mol in self.index.get(key):
                    if not score.get(mol):
                        score[mol] = 1
                    else:
                        score[mol] += 1

            maxscore = max(score.values())
            return map(lambda x: x[0], [x for x in score.iteritems() if x[1] == maxscore])


#-----------------------------------------------------------------------------------------------------------------------

mf = MoleculeFinder()