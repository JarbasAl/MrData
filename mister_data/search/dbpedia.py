import requests

from mister_data.search import DataSource


class DBPedia(DataSource):
    def __init__(self):
        # self hosted - https://github.com/dbpedia/lookup
        DataSource.__init__(self, "http://lookup.dbpedia.org/api/search/")

    def keyword_search(self, query):
        query = "KeywordSearch?QueryString=" + query
        return self.query(query)

    def prefix_search(self, query):
        query = "PrefixSearch?MaxHits=5&QueryString=" + query
        return self.query(query)

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

    def labels(self, query):
        """ return parsed result """
        results = self.keyword_search(query)["results"]
        triples = []
        for res in results:
            for cat in res["categories"]:
                triples.append((cat["label"], "uri", cat["uri"]))
                triples.append((res["label"], "categorie", cat["label"]))
            for cat in res["classes"]:
                triples.append((cat["label"], "uri", cat["uri"]))
                triples.append((res["label"], "isA", cat["label"]))
            triples.append((res["label"], "description", res["description"]))
            triples.append((res["label"], "uri", res["uri"]))

        return triples

    def query(self, query):
        """ return raw result (dict) """
        if "QueryString=" not in query:
            query = "KeywordSearch?QueryString=" + query
        return requests.get(self.base_url + query,
                            headers={"Accept": "application/json"}).json()


if __name__ == "__main__":
    from pprint import pprint

    engine = DBPedia()
    subject = "dog"
    pprint(engine.query(subject))
    pprint(engine.labels(subject))

