import requests

from mister_data.search import DataSource


class ConceptNet(DataSource):
    def __init__(self):
        DataSource.__init__(self, "http://api.conceptnet.io")

    def triples(self, query):
        """ return parsed result """
        obj = self.query(query)
        res = []
        for edge in obj["edges"]:
            subj = edge["start"]["@id"].replace("/c/en/", "")
            rel = edge["rel"]["@id"].replace("/r/", "")
            obj = edge["end"]["@id"].replace("/c/en/", "")

            res += [
                ("mrdata:" + subj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + obj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + rel, "rdf:type", "mrdata:property"),
                ("mrdata:" + subj + ":" + rel, "rdf:value", obj)
            ]

        return res

    def labels(self, query):
        """ return parsed result """
        obj = self.query(query)
        res = []
        for edge in obj["edges"]:
            subj = edge["start"]["label"]
            rel = edge["rel"]["label"]
            obj = edge["end"]["label"]
            res.append((subj, rel, obj))
        return res

    def query(self, query):
        """ return raw result (dict) """
        return requests.get('http://api.conceptnet.io/c/en/' + query).json()


if __name__ == "__main__":
    from pprint import pprint

    engine = ConceptNet()
    subject = "dog"
    #pprint(engine.query(subject))
    pprint(engine.labels(subject))

    #pprint(engine.normalized_triples(subject))
