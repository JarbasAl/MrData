from owlready2 import *
from os.path import join, expanduser, exists
from os import makedirs


class GenericOntology(object):
    def __init__(self, name, path=None):
        self.name = name.replace(".owl", "")
        if path is None:
            path = join(expanduser("~"), "mister_data", "owl")
            if not exists(path):
                makedirs(path)
            self.path = join(path, name + '.owl')
        else:
            self.path = path + "/" + self.name+".owl"
        self.onto = get_ontology(self.path)
        self.onto.load()

    def search(self, *args, **kwargs):
        return self.onto.search(*args, **kwargs)

    def search_one(self, *args, **kwargs):
        return self.onto.search_one(*args, **kwargs)

    def search_by_iri(self, iri):
        return self.onto.search(iri=iri)

    def search_by_type(self, typ):
        return self.onto.search(type=typ)

    def search_by_subclass_of(self, subclass_of):
        return self.onto.search(subclass_of=subclass_of)

    def search_by_is_a(self, is_a):
        return self.onto.search(is_a=is_a)

    def reason_hermit(self):
        with self.onto:
            sync_reasoner(infer_property_values=True)

    def reason_pellet(self):
        with self.onto:
            sync_reasoner_pellet()

    def as_sql(self):
        return None

    def from_sql(self, sql_db):
        return self

    def as_triples(self):
        return None

    def from_triples(self, triples):
        return self

    def commit(self):
        self.onto.save(self.path)
