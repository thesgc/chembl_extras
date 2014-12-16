chembl_extras
======

This is chembl_extras package developed at Chembl group, EMBL-EBI, Cambridge, UK.

This package provides two django custom migration commands:

    * generate_ora2pg_conf - generates configuration file for ora2pg (http://ora2pg.darold.net/) script based on given model.
    * generate_backbone_models - not implemented yet

Additionally, the package defines MoleculeFinder class which uses biopython suffix trie to index Inchies and search them by fragments.
It also provides Ontology (and derivatives) class to model different ontologies for future use.
