__author__ = 'mnowotka'

import gzip
from chembl_business_model.models import *


try:
    import cPickle as pickle
except ImportError:
    import pickle

#-----------------------------------------------------------------------------------------------------------------------

class Ontology:
    def containsTerm(self, term):
        pass

    def getIdsForTerm(self, term):
        pass

    def getAllTerms(self):
        pass

    def addTerm(self, term, id):
        pass

    def getOntology(self):
        pass

    def merge(self, ontology):
        pass

    def removeTerm(self, term):
        pass

    def fetch(self):
        pass

    def load(self, path):
        pass

    def save(self, path):
        pass

#-----------------------------------------------------------------------------------------------------------------------

class DictionaryBasedOntology(Ontology):
    def __init__(self):
        self.dict = {}

    def containsTerm(self, term):
        return term in self.dict

    def getIdsForTerm(self, term):
        return self.dict[term]

    def getAllTerms(self):
        return self.dict.keys()

    def addTerm(self, term, id):
        if term in dict:
            if isinstance(id, list):
                self.dict[term] += id
            else:
                self.dict[term].append(id)
        else:
            if isinstance(id, list):
                self.dict[term] = id
            else:
                self.dict[term] = [id]

    def getOntology(self):
        return self.dict.items()

    def merge(self, ontology):
        self.dict = dict(self.dict.items() + ontology.getOntology())

    def removeTerm(self, term):
        if term in self.dict:
            del self.dict[term]

    def save(self, path):
        f = gzip.open(path, 'wb')
        pickle.dump(self.dict, f)
        f.close()

    def load(self, path):
        f = gzip.open('file.txt.gz', 'rb')
        self.dict = pickle.load(f)
        f.close()

#-----------------------------------------------------------------------------------------------------------------------

class MoleculeOntology(Ontology):
    def fetch(self):
        for k, v in MoleculeDictionary.objects.filter(pref_name__isnull=False).values_list('pref_name', 'molregno'):
            self.addTerm(k, v)

#-----------------------------------------------------------------------------------------------------------------------

class MoleculeSynonymsOntology(Ontology):
    def fetch(self):
        for k, v in MoleculeSynonyms.objects.filter(synonyms__isnull=False).values_list('synonyms', 'molsyn_id'):
            self.addTerm(k, v)

#-----------------------------------------------------------------------------------------------------------------------

class TargetOntology(Ontology):
    def fetch(self):
        for k, v in TargetDictionary.objects.filter(pref_name__isnull=False).values_list('pref_name', 'tid'):
            self.addTerm(k, v)

#-----------------------------------------------------------------------------------------------------------------------

class AssayOntology(Ontology):
    def fetch(self):
        for k, v in Assays.objects.filter(description__isnull=False).values_list('description', 'assay_id'):
            self.addTerm(k, v)

#-----------------------------------------------------------------------------------------------------------------------

class ComponentSynonymsOntology(Ontology):
    def fetch(self):
        for k, v in ComponentSynonyms.objects.filter(component_synonym__isnull=False).values_list('component_synonym', 'compsyn_id'):
            self.addTerm(k, v)

#-----------------------------------------------------------------------------------------------------------------------