import os
import re
from os.path import join, dirname
from mister_data.store.sql import GenericSQLDatabase, MrDataSQLProperty, MrDataSQLThing
from mister_data.store.owl import GenericOntology
from owlready2 import World, sync_reasoner_hermit, sync_reasoner_pellet
import requests

ARCHIVES_PATH = join(dirname(dirname(__file__)), "archives")


def EYE_rest(data, rules="",
             query="{ ?a ?b ?c. } => { ?a ?b ?c. }.",
             server_url="http://eye.restdesc.org/"):
    """

    Args:
        data:
        rules:
        query:
        server_url:

    Returns:

    """
    if rules:
        data = data + "\n" + rules
    r = requests.post(server_url, json={"data": data, "query": query}).text
    return r


class SQLInspector(object):
    def __init__(self, db_name, path=ARCHIVES_PATH):
        self.name = db_name
        self.path = path

    def query(self, query):
        with GenericSQLDatabase(self.name, self.path) as db:
            return [a.as_json() for a in db.session.query(query)]

    def total_things(self):
        with GenericSQLDatabase(self.name, self.path) as db:
            return db.session.query(MrDataSQLThing).count()

    def search_by_name(self, name):
        with GenericSQLDatabase(self.name, self.path) as db:
            return [a.as_json() for a in
                    db.query(MrDataSQLThing).filter_by(name=name).all()]

    def search_by_type(self, thing_type):
        with GenericSQLDatabase(self.name, self.path) as db:
            return [a.as_json() for a in
                    db.query(MrDataSQLThing).filter_by(type=thing_type).all()]

    def search_by_id(self, thing_id):
        with GenericSQLDatabase(self.name, self.path) as db:
            return db.query(MrDataSQLThing).filter_by(id=thing_id).one().as_json()

    def search_by_property(self, name):
        things = []
        with GenericSQLDatabase(self.name, self.path) as db:
            for prop in db.query(MrDataSQLProperty).filter_by(name=name).all():
                things += prop.things
            things = [t.as_json() for t in things]
        return things

    def search_by_value(self, value):
        things = []
        with GenericSQLDatabase(self.name, self.path) as db:
            for prop in db.query(MrDataSQLProperty).filter_by(value=value).all():
                things += prop.things
            things = [t.as_json() for t in things]
        return things

    def as_owl(self):
        return None

    def from_owl(self, path):
        return self


class OntologyInspector(object):
    def __init__(self, owl_file, path, endpoint=None, inspector=None):
        self.owl_file = owl_file.replace(".owl", "")
        self.path = path
        self._onto = GenericOntology(join(self.path, self.owl_file))
        self.world = World()
        self.world.get_ontology(join(self.path,
                                     self.owl_file + ".owl")).load()

        self.endpoint = endpoint
        self.inspector = inspector or SPARQLQueries(endpoint, self)

        self.list_labels = set()  # An unique list of ontology labels
        self.superclass_for_class = {}
        self.__load_subclasses__()
        self.__nsmap = {}  ##mapping of namespaces

    @property
    def ontology(self):
        """ owlready2 ontology format """
        return self._onto.onto

    def reload_ontology(self):
        """ reload from disk """
        self._onto = GenericOntology(join(self.path, self.owl_file))

    def update_ontology(self, onto):
        """ owlready2 ontology format """
        self._onto.onto = onto

    def __get_owl_root_node__(self):
        try:
            from lxml import etree
        except:
            import xml.etree.cElementTree as etree
        owl_file = self.path + '/' + self.owl_file + ".owl"
        owl_root = etree.parse(owl_file).getroot()
        self.nsmap = owl_root.nsmap.copy()
        self.nsmap['xmlns'] = self.nsmap.pop(None)
        return owl_root

    def __load_subclasses__(self):
        owl_root = self.__get_owl_root_node__()
        for class_obj in owl_root.findall('{%s}Class' % owl_root.nsmap['owl']):
            onto_label = class_obj.get('{%s}about' % owl_root.nsmap['rdf'])
            self.list_labels.add(onto_label)
            subclass_of_obj = class_obj.find(
                '{%s}subClassOf' % owl_root.nsmap['rdfs'])
            if subclass_of_obj is not None:
                superclass_label = subclass_of_obj.get(
                    '{%s}resource' % owl_root.nsmap['rdf'])
                self.superclass_for_class[onto_label] = superclass_label

    def is_leaf_class(self, onto_label):
        """
        Checks if the ontology label provided (for instance http://dbpedia.org/ontology/SportsTeam) is a leaf in the DBpedia ontology tree or not
        It is a leaf if it is not super-class of any other class in the ontology
        @param onto_label: the ontology label
        @type onto_label: string
        @return: whether it is a leaf or not
        @rtype: bool
        """
        is_super_class = False
        for subclass, superclass in list(self.superclass_for_class.items()):
            if superclass == onto_label:
                is_super_class = True
                break
        if not is_super_class and onto_label not in self.list_labels:
            return None

        return not is_super_class

    def get_ontology_path(self, onto_label):
        '''
        Returns the path of ontology classes for the given ontology label (is-a relations)
        @param onto_label: the ontology label (could be http://dbpedia.org/ontology/SportsTeam or just SportsTeam)
        @type onto_label: str
        @return: list of ontology labels
        @rtype: list
        '''
        thing_label = '%sThing' % self.nsmap['owl']
        if onto_label == thing_label:
            return [thing_label]
        else:
            if self.nsmap[
                'xmlns'] not in onto_label:  # To allow things like "SportsTeam instead of http://dbpedia.org/ontology/SportsTeam
                onto_label = self.nsmap['xmlns'] + onto_label

            if onto_label not in self.superclass_for_class:
                return []
            else:
                super_path = self.get_ontology_path(
                    self.superclass_for_class[onto_label])
                super_path.insert(0, onto_label)
                return super_path

    def get_depth(self, onto_label):
        '''
        Returns the depth in the ontology hierarchy for the given ontology label (is-a relations)
        @param onto_label: the ontology label (could be http://dbpedia.org/ontology/SportsTeam or just SportsTeam)
        @type onto_label: str
        @return: depth
        @rtype: int
        '''
        path = self.get_ontology_path(onto_label)
        return len(path)

    def search(self, *args, **kwargs):
        return self.ontology.search(*args, **kwargs)

    def search_one(self, *args, **kwargs):
        return self.ontology.search_one(*args, **kwargs)

    def search_by_iri(self, iri):
        return self.ontology.search(iri=iri)

    def search_by_type(self, typ):
        return self.ontology.search(type=typ)

    def search_by_subclass_of(self, subclass_of):
        return self.ontology.search(subclass_of=subclass_of)

    def search_by_is_a(self, is_a):
        return self.ontology.search(is_a=is_a)

    def as_sql(self, query, name=None, path=None):
        """ search triples and export result in sql db"""
        name = name or query
        with GenericSQLDatabase(name, path) as db:
            triples = self.inspector.triples(query)
            for triple in triples:
                thing = triple["subject"]["value"]
                prop = triple["predicate"]["value"]
                value = triple["object"]["value"]
                t = db.add_thing(thing)
                p = db.add_property(prop, value=value)
                t.properties.append(p)
        return db

    def from_sql(self, path):
        return self

    def hermit_reason(self):
        """ load from disk, reason and return owlready2 ontology format"""
        self.world = World()
        onto = self.world.get_ontology(join(self.path,
                                            self.owl_file + ".owl")).load()
        sync_reasoner_hermit(self.world)
        return onto

    def pellet_reason(self):
        """ load from disk, reason and return owlready2 ontology format"""
        self.world = World()
        onto = self.world.get_ontology(join(self.path,
                                            self.owl_file + ".owl")).load()

        sync_reasoner_pellet(self.world)
        return onto

    def EYE_reason(self, data, rules):
        '''
        data = """
            @prefix ppl: <http://example.org/people#>.
            @prefix foaf: <http://xmlns.com/foaf/0.1/>.

            ppl:Cindy foaf:knows ppl:John.
            ppl:Cindy foaf:knows ppl:Eliza.
            ppl:Cindy foaf:knows ppl:Kate.
            ppl:Eliza foaf:knows ppl:John.
            ppl:Peter foaf:knows ppl:John.
        """

        rules = """
            @prefix foaf: <http://xmlns.com/foaf/0.1/>.

            {
                ?personA foaf:knows ?personB.
            }
            =>
            {
                ?personB foaf:knows ?personA.
            }.
        """

        output = """
            PREFIX ppl: <http://example.org/people#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>

            ppl:Cindy foaf:knows ppl:John.
            ppl:Cindy foaf:knows ppl:Eliza.
            ppl:Cindy foaf:knows ppl:Kate.
            ppl:Eliza foaf:knows ppl:John.
            ppl:Peter foaf:knows ppl:John.
            ppl:John foaf:knows ppl:Cindy.
            ppl:Eliza foaf:knows ppl:Cindy.
            ppl:Kate foaf:knows ppl:Cindy.
            ppl:John foaf:knows ppl:Eliza.
            ppl:John foaf:knows ppl:Peter.        """

        '''
        return EYE_rest(data, rules)


class SPARQLQueries(object):
    def __init__(self, endpoint, ontology):
        #self._onto = ontology
       # endpoint = endpoint or self._onto.path + "/sparql"
        self.__endpoint__ = endpoint
        self.__thisfolder__ = os.path.dirname(os.path.realpath(__file__))
        self.__cache_folder__ = join(ARCHIVES_PATH, "sparql_cache")

    def sparql_query(self, query):
        """
        ""SELECT ?p WHERE {
          <http://www.semanticweb.org/jiba/ontologies/2017/0/test#ma_pizza> <http://www.semanticweb.org/jiba/ontologies/2017/0/test#price> ?p .
        }""
        """
        my_world = World()
        onto = my_world.get_ontology(join(self._onto.path,
                                          self._onto.owl_file + ".owl")).load()
        graph = my_world.as_rdflib_graph()
        return list(graph.query(query))

    def sparql_query_owlready(self, query):
        """
        ""SELECT ?p WHERE {
          <http://www.semanticweb.org/jiba/ontologies/2017/0/test#ma_pizza> <http://www.semanticweb.org/jiba/ontologies/2017/0/test#price> ?p .
        }""
        """
        my_world = World()
        onto = my_world.get_ontology(join(self._onto.path,
                                          self._onto.owl_file + ".owl")).load()
        graph = my_world.as_rdflib_graph()
        return list(graph.query_owlready(query))

    def camel_to_word(self, text):
        words = re.findall('[A-Z][^A-Z]*', text)
        return " ".join(words)
