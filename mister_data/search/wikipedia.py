import wptools
from mister_data.search import DataSource


class Wikipedia(DataSource):
    def __init__(self):
        DataSource.__init__(self, "https://www.wikipedia.org")

    def labels(self, query):
        """ return parsed result """
        obj = self.query(query)
        triples = []
        for rel in obj:
            r = obj[rel]
            if isinstance(r, list):
                for o in r:
                    if isinstance(o, str):
                        triples.append((query, rel, o))
                    elif isinstance(o, dict):
                        for k in o:
                            triples.append((obj["title"] + " " + rel, k, o[k]))
            elif isinstance(r, dict):
                for k in r:
                    triples.append((obj["title"] + " " + rel, k, r[k]))
            elif isinstance(r, str):
                triples.append((query, rel, r))
        return triples

    def query(self, query):
        """ return raw result (dict) """
        res = {}
        try:
            res = wptools.page(subject, silent=True,
                                verbose=False).get_query().data
            removes = ["WARNINGS", "extract", "image", "length", "links",
                       "modified", "random", "redirected", "redirects",
                       "requests", "url_raw", "watchers", "assessments"]
            replaces = {"extext": "summary", "pageid": "wikipedia_pageid",
                        "wikibase": "wikibaseID", "url": "wikipedia_url",
                        "aliases": "alias"}
            for r in removes:
                res.pop(r)
            for r in replaces:
                res[replaces[r]] = res[r]
                res.pop(r)
        except LookupError:
            print("could not find wikipedia data for ", subject)
        return res


if __name__ == "__main__":
    from pprint import pprint

    engine = Wikipedia()
    subject = "dog"
    pprint(engine.query(subject))
    pprint(engine.labels(subject))
