from mister_data.search.conceptnet import ConceptNet
from pprint import pprint

engine = ConceptNet()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

from mister_data.search.dbpedia import DBPedia

engine = DBPedia()
pprint(engine.query(subject))
pprint(engine.labels(subject))

from mister_data.search.wikidata import Wikidata

engine = Wikidata()
pprint(engine.query(subject))
pprint(engine.labels(subject))

from mister_data.search.openie import Openie

engine = Openie()
pprint(engine.query(subject))
pprint(engine.labels(subject))