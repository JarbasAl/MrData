from mister_data.query import SPARQLQueries, OntologyInspector, ARCHIVES_PATH
import requests
from os.path import join, dirname
import hashlib
import pickle
import os
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

OWL_FILE = "dbpedia_2014.owl"


class DbpediaOntology(OntologyInspector):
    '''
    This class encapsulates the dbpedia ontology and gives acces to it
    '''

    def __init__(self, owl_file=OWL_FILE, path=ARCHIVES_PATH,
                 endpoint=None, inspector=None):
        self.path = path
        OntologyInspector.__init__(self, owl_file, path, endpoint, inspector)


class DbpediaEnquirer(SPARQLQueries):
    """
    This class allows to resource dbpedia using the Virtuoso SPARQL endpoint and gives access to different type of information
    """

    def __init__(self, endpoint='http://dbpedia.org/sparql', ontology=None):
        #ontology = ontology or DbpediaOntology()
        SPARQLQueries.__init__(self, endpoint, ontology)

    def _get_name_cached_file(self, query):
        if isinstance(query, str):
            query = query.encode('utf-8')
        cached_file = self.__cache_folder__ + '/' + hashlib.sha256(
            query).hexdigest()
        return cached_file

    def _get_name_cached_ontology_type(self, dblink):
        if isinstance(dblink, str):
            dblink = dblink.encode('utf-8')
        cached_file = self.__cache_folder__ + '/' + hashlib.sha256(
            dblink).hexdigest() + '.ontologytype'
        return cached_file

    def _my_query(self, this_query):
        cached_file = self._get_name_cached_file(this_query)
        if os.path.exists(cached_file):
            fd = open(cached_file, 'rb')
            results = pickle.load(fd)
            fd.close()
        else:
            sparql = SPARQLWrapper(self.__endpoint__)
            sparql.setQuery(this_query)
            sparql.setReturnFormat(JSON)
            query = sparql.query()
            # resource.setJSONModule(json)
            results = query.convert()['results']['bindings']
            if not os.path.exists(self.__cache_folder__):
                os.mkdir(self.__cache_folder__)
            fd = open(cached_file, 'wb')
            pickle.dump(results, fd, protocol=-1)
            fd.close()
        return results

    def _fix_link(self, dblink):
        # fix labels to link
        if not dblink.startswith("http"):

            if " " in dblink:
                dblink = dblink.split(" ")
                for idx, d in enumerate(dblink):
                    if not dblink[idx]:
                        continue
                    if dblink[idx][0].islower():
                        dblink[idx] = dblink[idx][0].upper() + dblink[idx][1:]
                dblink = "_".join(dblink)
            elif dblink[0].islower():
                dblink = dblink[0].upper() + dblink[1:]
            dblink = "http://dbpedia.org/resource/" + dblink
        return dblink

    def get_deepest_ontology_class(self, resource):
        """
        Given a uri (http://dbpedia.org/resource/Tom_Cruise) gets all the
        possible ontology classes from dbpedia,
        calculates the depth of each on in the ontology and returns the deepest one
        @param resource: the uri link
        @type resource: string
        @return: the deespest uri ontology label
        @rtype: string
        """
        deepest = None
        onto_labels = self.search_labels(resource)
        pair_label_path = []
        for ontolabel in onto_labels:
            this_path = self._onto.get_ontology_path(
                ontolabel["object"]["value"])
            pair_label_path.append((ontolabel, len(this_path)))
        if len(pair_label_path) > 0:
            deepest = sorted(pair_label_path, key=lambda t: -t[1])[0][0]
        return deepest

    def search_triples(self, resource):
        """
        Returns triples for uri link (the type
        http://www.w3.org/1999/02/22-rdf-syntax-ns#type will be checked
        and only labels containing  http://dbpedia.org/ontology/* will be returned
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: list of ontology labels
        @rtype: list
        """
        triples = []
        try:
            json_result = self.search_resource(resource)
            for dictionary in json_result:
                triples.append(dictionary)
        except QueryBadFormed:
            raise ValueError
        return triples

    def triples(self, query):
        """ return parsed result """
        results = self.search_triples(query)
        triples = []
        for r in results:
            subj = r["subject"]["value"]
            rel = r["predicate"]["value"]
            obj = r["object"]["value"]
            triples += [
                ("mrdata:" + subj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + obj, "rdf:type", "mrdata:thing"),
                ("mrdata:" + rel, "rdf:type", "mrdata:property"),
                ("mrdata:" + subj, "mrdata_prop:" + rel, "mrdata:" + obj)
            ]

        return triples

    def is_person(self, resource):
        """
        Returns True if the link has rdf:type dbpedia:Person, False otherwise
        @param dblink" a dbpedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: whether the dblink is a dbpedia person
        @rtype: str
        """
        dbpedia_json = self.search_resource(resource)
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object = dictionary['object']['value']

            if predicate == 'rdf:type' and object == 'http://dbpedia.org/ontology/person':
                return True
        return False

    def search_resource(self, resource):
        """
        Returns a dictionary with all the triple relations stored in DBPEDIA for the given entity
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: dictionary with triples
        @rtype: dict
        """
        resource = self._fix_link(resource)
        query = """
                       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                       SELECT ?predicate ?object
                       WHERE { <%s> ?predicate ?object }
                       """ % resource
        results = self._my_query(query)
        for idx, r in enumerate(results):
            results[idx]["subject"] = {"type": "uri", "value": resource}
        return results

    def search_unique_values(self, resource):
        """
        Perform a check whether a dbpedia resource is unique
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: dictionary with triples
        @rtype: dict
        """
        dblink = self._fix_link(resource)
        query = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?predicate ?object
                WHERE { <%s> ?predicate ?object . FILTER NOT EXISTS { <%s> <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o } }
                """ % (dblink, dblink)
        results = self._my_query(query)
        for idx, r in enumerate(results):
            results[idx]["subject"] = {"type": "uri", "value": dblink}
        return results

    def search_labels(self, resource):
        """
        Returns the DBpedia ontology labels for the given DBpedia link (the type http://www.w3.org/1999/02/22-rdf-syntax-ns#type will be checked
        and only labels containing  http://dbpedia.org/ontology/* will be returned
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: list of ontology labels
        @rtype: list
        """
        resource = self._fix_link(resource)
        ontology_labels = []
        try:
            json_result = self.search_resource(resource)

            ontology_labels = []
            for dictionary in json_result:
                predicate = dictionary['predicate']['value']
                if predicate.endswith("#type"):
                    ontology_labels.append(dictionary)
        except QueryBadFormed:
            raise ValueError
        return ontology_labels[1:]

    def get_wiki_page_url(self, dblink):
        """
        Returns the wikipedia page url for the given DBpedia link (the relation 'http://xmlns.com/foaf/0.1/isPrimaryTopicOf is checked)
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: the wikipedia URL
        @rtype: str
        """

        dbpedia_json = self.search_resource(dblink)
        lang = wikipage = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object = dictionary['object']['value']

            if predicate == 'http://xmlns.com/foaf/0.1/isPrimaryTopicOf':
                wikipage = object
                break

        return wikipage

    def get_wiki_page_id(self, resource):
        """
        Returns the wikipedia page id for the given DBpedia link (the relation http://dbpedia.org/ontology/wikiPageID is checked)
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: the wikipedia identifier
        @rtype: str
        """

        dbpedia_json = self.search_resource(resource)
        lang = wikipageid = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object = dictionary['object']['value']

            if predicate == 'http://dbpedia.org/ontology/wikiPageID':
                wikipageid = object
                break

        return wikipageid

    def get_language(self, resource):
        """
        Returns the language given a DBpedia link (xml:lang predicate)
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: the language (or None if there is no lang)
        @rtype: str
        """
        dbpedia_json = self.search_resource(resource)
        lang = None
        for dictionary in dbpedia_json:
            if 'xml:lang' in dictionary['object']:
                lang = dictionary['object']['xml:lang']
                break
        return lang

    def get_wordnet_type(self, resource):
        """
        Returns the wordnet type for the given DBpedia link (the relation http://dbpedia.org/property/wordnet_type is checked)
        It returns the last part of the WN type ((from http://www.w3.org/2006/03/wn/wn20/instances/synset-actor-noun-1 --> synset-actor-noun-1 )
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: the wordnet type
        @rtype: str
        """
        dbpedia_json = self.search_resource(resource)
        wordnet_type = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object = dictionary['object']['value']

            if predicate == 'http://dbpedia.org/property/wordnet_type':
                return dictionary

        return wordnet_type

    def external_urls_for_resource(self, resource):
        """
        Returns the DBpedia synonyms for the given DBpedia link (the type http://www.w3.org/1999/02/22-rdf-syntax-ns#type will be checked
        and only labels containing  http://dbpedia.org/ontology/* will be returned
        @param resource: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type resource: str
        @return: list of ontology labels
        @rtype: list
        """
        urls = []
        try:
            resource = self._fix_link(resource)
            dbpedia_json = self.search_resource(resource)
            for dictionary in dbpedia_json:
                predicate = dictionary['predicate']['value']
                if predicate.endswith("/wikiPageExternalLink"):
                    object = dictionary['object']['value']
                    if object and object not in urls:
                        urls.append(object)
        except QueryBadFormed:
            raise ValueError
        return urls

    @staticmethod
    def scrap_resource_page(link):
        u = link.replace("http://dbpedia.org/resource/",
                         "http://dbpedia.org/data/") + ".json"
        data = requests.get(u)
        json_data = data.json()
        return json_data[link]

    def normalized_triples(self, query):
        triples = self.triples(query)
        normalized_triples = []
        # remove dups
        for t in triples:
            if t not in normalized_triples:
                normalized_triples.append(t)

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
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#', ""), t[1],
                                           t[2])
            if "http://dbpedia.org/resource/" in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    "http://dbpedia.org/resource/", ""))
            if "http://dbpedia.org/ontology/" in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    "http://dbpedia.org/ontology/", ""))
            if "http://schema.org/" in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    "http://schema.org/", ""))
            if "http://purl.org/linguistics/gold/" in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    "http://purl.org/linguistics/gold/", ""))
            if 'http://www.w3.org/2002/07/owl#' in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    'http://www.w3.org/2002/07/owl#', ""))
            if 'http://www.w3.org/1999/02/22-rdf-syntax-ns#' in t[2]:
                normalized_triples[idx] = (t[0], t[1], t[2].replace(
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#', ""))
        return normalized_triples


if __name__ == '__main__':
    from pprint import pprint

    my_dbpedia = DbpediaEnquirer()
    resource = "Person"

    result = my_dbpedia.search_labels(resource)
    pprint(result)

    # result = my_dbpedia.get_deepest_ontology_class(resource)
    # pprint(result)

    result = my_dbpedia.search_unique_values(resource)
    pprint(result)

    result = my_dbpedia.search_resource(resource)
    pprint(result)

    triples = my_dbpedia.normalized_triples(resource)
    pprint(triples)

    urls = my_dbpedia.external_urls_for_resource(resource)
    pprint(urls)

