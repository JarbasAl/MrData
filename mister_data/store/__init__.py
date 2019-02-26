from mister_data.store.sql import GenericSQLDatabase
from mister_data.store.owl import GenericOntology
from mister_data.search import DataSource


class GenericTripleStore(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self._triples = []

    def normalized_triples(self, query):
        triples = self._triples
        normalized_triples = triples

        # cleanup uris
        for idx, t in enumerate(normalized_triples):
            if "http://dbpedia.org/resource/" in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    "http://dbpedia.org/resource/", ""), t[1], t[2])
            if "http://dbpedia.org/ontology/" in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    "http://dbpedia.org/ontology/", ""), t[1], t[2])
            if "http://schema.org/" in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    "http://schema.org/", ""), t[1], t[2])
            if "http://purl.org/linguistics/gold/" in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    "http://purl.org/linguistics/gold/", ""), t[1], t[2])
            if 'http://www.w3.org/2002/07/owl#' in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    'http://www.w3.org/2002/07/owl#', ""), t[1], t[2])
            if 'http://www.w3.org/1999/02/22-rdf-syntax-ns#' in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#', ""),
                                           t[1], t[2])
            if 'https://www.wikidata.org/wiki/' in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    'https://www.wikidata.org/wiki/', ""), t[1], t[2])
            if 'https://en.wikipedia.org/wiki/' in t[0]:
                normalized_triples[idx] = (t[0].replace(
                    'https://en.wikipedia.org/wiki/', ""), t[1], t[2])

        # remove dups
        triples = []
        for idx, t in enumerate(normalized_triples):
            if t not in triples:
                triples.append(t)

        return triples

    def from_data_source(self, source=None):
        assert isinstance(source, DataSource)
        self._triples = source.normalized_triples(self.name)
        return self

    def as_sql(self):
        return GenericSQLDatabase(self.name, self.path).from_triples(self._triples)

    def from_sql(self, sql_db=None):
        with sql_db or GenericSQLDatabase(self.name, self.path) as db:
            self._triples = sql_db.as_triples()
        return self

    def as_owl(self):
        onto = GenericOntology(self.path + "/" + self.name + ".owl").from_triples(self._triples)
        return onto

    def from_owl(self, owl=None):
        if isinstance(owl, str) and owl.endswith(".owl"):
            onto = GenericOntology(owl)
        else:
            onto = owl or GenericOntology(self.path + "/" + self.name + ".owl")
        self._triples = onto.as_triples()
        return self

    def as_triples(self):
        return self._triples

    def from_triples(self, triples):
        self._triples = triples
        return self
