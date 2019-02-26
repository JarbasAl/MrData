


class DataSource(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def keyword_search(self, query):
        """ keyword triples, exact matches """
        return self.query(query)

    def prefix_search(self, query):
        """ prefix triples, partial matches """
        return self.query(query)

    def sparql_query(self, query):
        """ perform sparql resource if supported"""
        return None

    def sql_query(self, query):
        """ perform sql resource if supported """
        return None

    def labels(self, query):
        """ return list of triples (tuple of strings) """
        return []

    def triples(self, query):
        """ return parsed result """
        results = self.labels(query)
        triples = []
        for subj, rel, obj in results:
            triples += [
                ("mrdata:" + subj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + obj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + rel, "rdf:type", "mrdata:property"),
                ("mrdata:" + subj + ":" + rel, "rdf:value", obj)
            ]

        return triples

    def normalized_triples(self, query):
        triples = self.triples(query)
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

    def query(self, query):
        """ return raw result """
        return None

    def as_owl(self, query, path=None):
        """ search triples and export result in owl file"""
        return path

    def as_sql(self, query, name, path=None):
        """ search triples and export result in sql db"""
        from mister_data.store.sql import GenericSQLDatabase
        with GenericSQLDatabase(name, path) as db:
            triples = self.triples(query)
            for thing, prop, value in triples:
                t = db.add_thing(thing)
                p = db.add_property(prop, value=value)
                t.properties.append(p)
        return db