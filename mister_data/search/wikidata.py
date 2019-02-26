import wptools
from mister_data.search import DataSource


class Wikidata(DataSource):
    def __init__(self):
        DataSource.__init__(self, "https://www.wikidata.org")

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
        base = wptools.page(query, silent=True, verbose=False).get_parse().data["wikibase"]
        page = wptools.page(wikibase=base).get_wikidata().data
        desired = ["aliases", "what", "label", "title", "labels",
                   "wikidata_pageid", "description"]
        res = page["wikidata"]
        for k in desired:
            if k in page.keys():
                if isinstance(page[k], str):
                    res[k] = page[k]
                elif k == "labels":
                    res["label"] = [label for label in page[k]]
                elif k == "aliases":
                    res["alias"] = [label for label in page[k]]
        return res


if __name__ == "__main__":
    from pprint import pprint

    engine = Wikidata()
    subject = "dog"
    pprint(engine.labels(subject))
    pprint(engine.query(subject))
