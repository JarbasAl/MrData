import requests

from mister_data.search import DataSource


class Genesis(DataSource):
    def __init__(self):
        # use the source https://github.com/dice-group/GENESIS
        DataSource.__init__(self, "http://genesis.aksw.org/api/search")

    def labels(self, query):
        """ return parsed result """
        results = self.query(query)
        triples = []
        for res in results:
            entry = res["title"]
            for k in res:
                triples.append((entry, k, res[k]))
        return triples

    def query(self, query):
        """ return raw result (dict) """
        data = {"q": query}
        return requests.post(self.base_url, json=data).json()


if __name__ == "__main__":
    from pprint import pprint

    engine = Genesis()
    subject = "dog"
    pprint(engine.query(subject))
    pprint(engine.labels(subject))

