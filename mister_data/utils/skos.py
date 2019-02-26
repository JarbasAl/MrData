__version__ = '0.1.1'

from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Table, Column, Integer, String, Date, Float, ForeignKey, event
from sqlalchemy import Table, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.orm.collections import collection
import collections
import logging

logger = logging.getLogger(__name__)


def info(*args, **kwargs):
    logger.info(*args, **kwargs)


def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)


# Create a SQLAlchemy declarative base class using our metaclass
Base = declarative_base()

# association tables for many to many joins
concept_broader = Table('concept_broader', Base.metadata,
                        Column('broader_uri', String(255),
                               ForeignKey('concept.uri')),
                        Column('narrower_uri', String(255),
                               ForeignKey('concept.uri'))
                        )

concept_synonyms = Table('concept_synonyms', Base.metadata,
                         Column('left_uri', String(255),
                                ForeignKey('concept.uri')),
                         Column('right_uri', String(255),
                                ForeignKey('concept.uri'))
                         )

concept_related = Table('concept_related', Base.metadata,
                        Column('left_uri', String(255),
                               ForeignKey('concept.uri')),
                        Column('right_uri', String(255),
                               ForeignKey('concept.uri'))
                        )

concepts2schemes = Table('concepts2schemes', Base.metadata,
                         Column('scheme_uri', String(255),
                                ForeignKey('concept_scheme.uri')),
                         Column('concept_uri', String(255),
                                ForeignKey('concept.uri'))
                         )

concepts2collections = Table('concepts2collections', Base.metadata,
                             Column('collection_uri', String(255),
                                    ForeignKey('collection.uri')),
                             Column('concept_uri', String(255),
                                    ForeignKey('concept.uri'))
                             )


class RecursionError(Exception):
    pass


# This function is necessary as the first option described at
# <http://groups.google.com/group/sqlalchemy/browse_thread/thread/b4eaef1bdf132cdc?pli=1>
# for a solution to self-referential many-to-many relationships using
# the same property does not seem to be writable.
def _create_attribute_mapping(name):
    """
    Factory function creating a class for attribute mapping

    The generated classes provide an interface for a bi-directional
    relationship between synonymous attributes in a `Concept` class.
    """

    class AttributeJoin(collections.MutableSet, collections.Mapping):

        def __init__(self, concept):
            self._left = getattr(concept, '_%s_left' % name)
            self._right = getattr(concept, '_%s_right' % name)

        # Implement the interface for `collections.Iterable`
        def __iter__(self):
            self._left.update(self._right)
            return iter(self._left)

        # Implement the interface for `collections.Container`
        def __contains__(self, value):
            return value in self._left or value in self._right

        # Implement the interface for `collections.Sized`
        def __len__(self):
            return len(set(list(self._left.keys()) + list(self._right.keys())))

        # Implement the interface for `collections.MutableSet`
        def add(self, value):
            self._left.add(value)

        def discard(self, value):
            self._left.discard(value)
            self._right.discard(value)

        def pop(self):
            try:
                value = self._concepts._synonyms_left.pop()
            except KeyError:
                value = self._concepts._synonyms_right.pop()
                self._concepts._synonyms_left.discard(value)
            else:
                self._concepts._synonyms_right.discard(value)
            return value

        # Implement the interface for `collections.Mapping` with the
        # ability to delete items as well

        def __getitem__(self, key):
            try:
                return self._left[key]
            except KeyError:
                pass

            try:
                return self._right[key]
            except KeyError as e:
                raise e

        def __delitem__(self, key):
            deleted = False
            try:
                del self._left[key]
            except KeyError:
                pass
            else:
                deleted = True

            try:
                del self._right[key]
            except KeyError as e:
                if not deleted:
                    raise e

        def __repr__(self):
            return repr(dict(self))

        def __str__(self):
            return str(dict(self))

        def __eq__(self, other):
            return (
                    self._right == other._right and
                    self._left == other._left
            )

    return AttributeJoin


class Concepts(collections.Mapping, collections.MutableSet):
    """
    A collection of Concepts

    This is a composition of the `collections.MutableSet` and
    `collections.Mapping` classes. It is *not* a `skos:Collection`
    implementation.
    """

    def __init__(self, values=None):
        self._concepts = {}
        if values:
            self.update(values)

    # Implement the interface for `collections.Iterable`
    def __iter__(self):
        return iter(self._concepts)

    # Implement the interface for `collections.Container`
    def __contains__(self, value):
        try:
            # if it's a Concept, get the Concept's key to test
            value = value.uri
        except AttributeError:
            pass
        return value in self._concepts

    # Implement the interface for `collections.Sized`
    def __len__(self):
        return len(self._concepts)

    # Implement the interface for `collections.MutableSet`
    def add(self, value):
        self._concepts[value.uri] = value

    def discard(self, value):
        try:
            del self._concepts[value.uri]
        except KeyError:
            pass

    def pop(self):
        key, value = self._concepts.popitem()
        return value

    # Implement the interface for `collections.Mapping` with the
    # ability to delete items as well

    def __getitem__(self, key):
        return self._concepts[key]

    def __delitem__(self, key):
        self.discard(
            self._concepts[key])  # remove through an instrumented method

    def update(self, concepts):
        """
        Update the concepts from another source

        The argument can be a dictionary-like container of concepts or
        a sequence of concepts.
        """
        if not isinstance(concepts, collections.Mapping):
            iterator = iter(concepts)
        else:
            iterator = iter(concepts.values())
        for value in iterator:
            self.add(value)

    def __eq__(self, other):
        try:
            # if comparing another Concept, match against the
            # underlying dictionary
            return self._concepts == other._concepts
        except AttributeError:
            pass
        return self._concepts == other

    def __str__(self):
        return str(self._concepts)

    def __repr__(self):
        return repr(self._concepts)


class InstrumentedConcepts(Concepts):
    """
    Adapted `Concepts` class for use in SQLAlchemy relationships
    """

    # See <http://docs.sqlalchemy.org/en/latest/orm/collections.html>
    # for details on custom collections. This also uses the "trivial
    # subclass" trick detailed at
    # <http://docs.sqlalchemy.org/en/latest/orm/collections.html#instrumentation-and-custom-types>.

    @collection.iterator
    def itervalues(self):
        return iter(super(InstrumentedConcepts, self).values())

    @collection.appender
    def add(self, *args, **kwargs):
        return super(InstrumentedConcepts, self).add(*args, **kwargs)

    @collection.remover
    def discard(self, *args, **kwargs):
        return super(InstrumentedConcepts, self).discard(*args, **kwargs)

    @collection.converter
    @collection.internally_instrumented
    def update(self, concepts):
        """
        Update the concepts from another source

        The argument can be a dictionary-like container of concepts or
        a sequence of concepts.
        """
        if not isinstance(concepts, collections.Mapping):
            return iter(concepts)
        return iter(concepts.values())


_Synonyms = _create_attribute_mapping('synonyms')
_Related = _create_attribute_mapping('related')


class Object(Base):
    __tablename__ = 'object'
    _discriminator = Column('class', String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'object',
        'polymorphic_on': _discriminator
    }

    uri = Column(String(255), primary_key=True, nullable=False)

    def __init__(self, uri):
        self.uri = uri


class Concept(Object):
    __tablename__ = 'concept'
    __mapper_args__ = {'polymorphic_identity': 'concept'}

    uri = Column(String(255), ForeignKey('object.uri'), primary_key=True)
    prefLabel = Column(String(50), nullable=False)
    definition = Column(Text)
    notation = Column(String(50))
    altLabel = Column(String(50))

    def __init__(self, uri, prefLabel=None, definition=None, notation=None,
                 altLabel=None):
        super(Concept, self).__init__(uri)
        prefLabel = prefLabel or uri
        self.prefLabel = prefLabel
        self.definition = definition
        self.notation = notation
        self.altLabel = altLabel

    # many to many Concept <-> Concept representing broadness <->
    # narrowness
    broader = relationship(
        'Concept',
        secondary=concept_broader,
        primaryjoin=uri == concept_broader.c.narrower_uri,
        secondaryjoin=uri == concept_broader.c.broader_uri,
        collection_class=InstrumentedConcepts,
        backref=backref('narrower', collection_class=InstrumentedConcepts))

    # many to many Concept <-> Concept representing relationship
    _related_left = relationship(
        'Concept',
        secondary=concept_related,
        primaryjoin=uri == concept_related.c.left_uri,
        secondaryjoin=uri == concept_related.c.right_uri,
        collection_class=InstrumentedConcepts,
        backref=backref('_related_right',
                        collection_class=InstrumentedConcepts))

    # many to many Concept <-> Concept representing exact matches
    _synonyms_left = relationship(
        'Concept',
        secondary=concept_synonyms,
        primaryjoin=uri == concept_synonyms.c.left_uri,
        secondaryjoin=uri == concept_synonyms.c.right_uri,
        collection_class=InstrumentedConcepts,
        backref=backref('_synonyms_right',
                        collection_class=InstrumentedConcepts))

    def _getSynonyms(self):
        return _Synonyms(self)

    def _setSynonyms(self, values):
        self._synonyms_left = values
        self._synonyms_right = {}

    synonyms = synonym('_synonyms_left',
                       descriptor=property(_getSynonyms, _setSynonyms))

    def _getRelated(self):
        return _Related(self)

    def _setRelated(self, values):
        self._related_left = values
        self._related_right = {}

    related = synonym('_related_left',
                      descriptor=property(_getRelated, _setRelated))

    def __repr__(self):
        return "<%s('%s')>" % (self.__class__.__name__, self.uri)

    def __hash__(self):
        return hash(''.join((v for v in (getattr(self, attr) for attr in (
            'uri', 'prefLabel', 'definition', 'notation', 'altLabel')) if v)))

    def __eq__(self, other):
        try:
            return min([getattr(self, attr) == getattr(other, attr) for attr in
                        ('uri', 'prefLabel', 'definition', 'notation',
                         'altLabel')])
        except AttributeError:
            return False


class ConceptScheme(Object):
    """
    Represents a set of Concepts

    `skos:ConceptScheme` is a set of concepts, optionally including
    statements about semantic relationships between those
    concepts. Thesauri, classification schemes, subject-heading lists,
    taxonomies, terminologies, glossaries and other types of
    controlled vocabulary are all examples of concept schemes
    """

    __tablename__ = 'concept_scheme'
    __mapper_args__ = {'polymorphic_identity': 'scheme'}

    uri = Column(String(255), ForeignKey('object.uri'), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    def __init__(self, uri, title, description=None):
        super(ConceptScheme, self).__init__(uri)
        self.title = title
        self.description = description

    concepts = relationship(
        'Concept',
        secondary=concepts2schemes,
        collection_class=InstrumentedConcepts,
        backref=backref('schemes', collection_class=InstrumentedConcepts))

    def __repr__(self):
        return "<%s('%s')>" % (self.__class__.__name__, self.uri)

    def __hash__(self):
        return hash(''.join(
            (getattr(self, attr) for attr in ('uri', 'title', 'description'))))

    def __eq__(self, other):
        return min([getattr(self, attr) == getattr(other, attr) for attr in
                    ('uri', 'title', 'description', 'concepts')])


class Collection(Object):
    """
    Represents a skos:Collection
    """

    __tablename__ = 'collection'
    __mapper_args__ = {'polymorphic_identity': 'collection'}

    uri = Column(String(255), ForeignKey('object.uri'), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)

    def __init__(self, uri, title, description=None, date=None):
        super(Collection, self).__init__(uri)
        self.title = title
        self.description = description
        self.date = date

    members = relationship(
        'Concept',
        secondary=concepts2collections,
        collection_class=InstrumentedConcepts,
        backref=backref('collections', collection_class=InstrumentedConcepts))

    def __repr__(self):
        return "<%s('%s')>" % (self.__class__.__name__, self.uri)

    def __hash__(self):
        return hash(''.join((str(getattr(self, attr)) for attr in
                             ('uri', 'title', 'description', 'date'))))

    def __eq__(self, other):
        try:
            return min([getattr(self, attr) == getattr(other, attr) for attr in
                        ('uri', 'title', 'description', 'members', 'date')])
        except AttributeError:
            return False


import rdflib
from itertools import chain, islice


class RDFLoader(collections.Mapping):
    """
    Loads an RDF graph into the Python SKOS object model

    This class provides a mappable interface, with URIs as keys and
    the objects themselves as values.

    Use the `RDFBuilder` class to convert the Python SKOS objects back
    into a RDF graph.
    """

    def __init__(self, graph, max_depth=0, flat=False, normalise_uri=str,
                 lang=None):
        if not isinstance(graph, rdflib.Graph):
            raise TypeError(
                '`rdflib.Graph` type expected for `graph` argument, found: %s' % type(
                    graph))

        try:
            self.max_depth = float(max_depth)
        except (TypeError, ValueError):
            raise TypeError(
                'Numeric type expected for `max_depth` argument, found: %s' % type(
                    max_depth))

        self.flat = bool(flat)

        if not callable(normalise_uri):
            raise TypeError('callable expected for `normalise_uri` argument')
        self.normalise_uri = normalise_uri

        self.load(graph, lang)  # convert the graph to our object model

    def _dcDateToDatetime(self, date):
        """
        Convert a Dublin Core date to a datetime object
        """
        from iso8601 import parse_date, ParseError
        try:
            return parse_date(date)
        except ParseError:
            return None

    def _resolveGraph(self, graph, depth=0, resolved=None):
        """
        Resolve external RDF resources
        """
        if depth >= self.max_depth:
            return

        if resolved is None:
            resolved = set()

        resolvable_predicates = (
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#broader'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#narrower'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),
            rdflib.URIRef('http://www.w3.org/2006/12/owl2-xml#sameAs'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#related'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#member'),
        )

        resolvable_objects = (
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#ConceptScheme'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#Concept'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#Collection'),
            rdflib.URIRef('http://www.w3.org/2004/02/skos/core#hasTopConcept'),
        )

        normalise_uri = self.normalise_uri
        # add existing resolved objects
        for object_ in resolvable_objects:
            resolved.update((normalise_uri(subject) for subject in
                             graph.subjects(predicate=rdflib.URIRef(
                                 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                                 object=object_)))

        unresolved = set()
        for predicate in resolvable_predicates:
            for subject, object_ in graph.subject_objects(predicate=predicate):
                uri = normalise_uri(object_)
                if uri not in resolved:
                    unresolved.add(uri)

        # flag the unresolved as being resolved, as that is what
        # happens next; flagging them now prevents duplicate
        # resolutions!
        resolved.update(unresolved)

        for uri in unresolved:
            info('parsing %s', uri)
            subgraph = graph.parse(uri)
            self._resolveGraph(subgraph, depth + 1, resolved)

    def _iterateType(self, graph, type_):
        """
        Iterate over all subjects of a specific SKOS type
        """
        predicate = rdflib.URIRef(
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        object_ = rdflib.URIRef(
            'http://www.w3.org/2004/02/skos/core#%s' % type_)
        for subject in graph.subjects(predicate=predicate, object=object_):
            yield subject

    def _get_value_for_lang(self, graph, subject, predicate, lang):
        objects = graph.objects(subject=subject, predicate=predicate)
        if not objects:
            return None

        for obj in objects:
            if hasattr(obj, "language") and obj.language == lang:
                return obj.value

        return None

    def _loadConcepts(self, graph, cache, lang):
        # generate all the concepts
        concepts = set()
        normalise_uri = self.normalise_uri
        prefLabel = rdflib.URIRef(
            'http://www.w3.org/2004/02/skos/core#prefLabel')
        definition = rdflib.URIRef(
            'http://www.w3.org/2004/02/skos/core#definition')
        notation = rdflib.URIRef(
            'http://www.w3.org/2004/02/skos/core#notation')
        altLabel = rdflib.URIRef(
            'http://www.w3.org/2004/02/skos/core#altLabel')

        default_label = [[None, type('obj', (object,), {'value': ""})]]

        for subject in self._iterateType(graph, 'Concept'):
            uri = normalise_uri(subject)

            # Check for a preferredLabel in our desired language
            label_list = graph.preferredLabel(subject, lang=lang,
                                              default=default_label)

            label = str(label_list[0][1].value)

            defn = self._get_value_for_lang(graph, subject, definition, lang)
            alt = self._get_value_for_lang(graph, subject, altLabel, lang)

            notn = str(graph.value(subject=subject, predicate=notation))

            debug('creating Concept %s', uri)
            cache[uri] = Concept(uri, label, defn, notn, alt)
            concepts.add(uri)

        attrs = {
            rdflib.URIRef(
                'http://www.w3.org/2004/02/skos/core#narrower'): 'narrower',
            rdflib.URIRef(
                'http://www.w3.org/2004/02/skos/core#broader'): 'broader',
            rdflib.URIRef(
                'http://www.w3.org/2004/02/skos/core#related'): 'related',
            rdflib.URIRef(
                'http://www.w3.org/2004/02/skos/core#exactMatch'): 'synonyms',
            rdflib.URIRef(
                'http://www.w3.org/2006/12/owl2-xml#sameAs'): 'synonyms'
        }
        for predicate, attr in attrs.items():
            for subject, object_ in graph.subject_objects(predicate=predicate):
                try:
                    match = cache[normalise_uri(object_)]
                except KeyError:
                    continue
                debug('adding %s to %s as %s', object_, subject, attr)
                getattr(cache[normalise_uri(subject)], attr).add(match)

        return concepts

    def _loadCollections(self, graph, cache):
        # generate all the collections
        collections = set()
        normalise_uri = self.normalise_uri
        pred_titles = [rdflib.URIRef('http://purl.org/dc/terms/title'),
                       rdflib.URIRef('http://purl.org/dc/elements/1.1/title')]
        pred_descriptions = [
            rdflib.URIRef('http://purl.org/dc/terms/description'),
            rdflib.URIRef('http://purl.org/dc/elements/1.1/description')]
        pred_dates = [rdflib.URIRef('http://purl.org/dc/terms/date'),
                      rdflib.URIRef('http://purl.org/dc/elements/1.1/date')]
        for subject in self._iterateType(graph, 'Collection'):
            uri = normalise_uri(subject)
            # create the basic concept
            title = str(self._valueFromPredicates(graph, subject, pred_titles))
            description = str(
                self._valueFromPredicates(graph, subject, pred_descriptions))
            date = self._dcDateToDatetime(
                self._valueFromPredicates(graph, subject, pred_dates))
            debug('creating Collection %s', uri)
            cache[uri] = Collection(uri, title, description, date)
            collections.add(uri)

        for subject, object_ in graph.subject_objects(predicate=rdflib.URIRef(
                'http://www.w3.org/2004/02/skos/core#member')):
            try:
                member = cache[normalise_uri(object_)]
            except KeyError:
                continue
            debug('adding %s to %s as a member', object_, subject)
            cache[normalise_uri(subject)].members.add(member)

        return collections

    def _valueFromPredicates(self, graph, subject, predicates):
        """
        Given a list of predicates return the first value from a graph that is not None
        """
        for predicate in predicates:
            value = graph.value(subject=subject, predicate=predicate)
            if value: return value
        return None

    def _loadConceptSchemes(self, graph, cache):
        # generate all the schemes
        schemes = set()
        normalise_uri = self.normalise_uri
        pred_titles = [rdflib.URIRef('http://purl.org/dc/terms/title'),
                       rdflib.URIRef('http://purl.org/dc/elements/1.1/title')]
        pred_descriptions = [
            rdflib.URIRef('http://purl.org/dc/terms/description'),
            rdflib.URIRef('http://purl.org/dc/elements/1.1/description')]
        for subject in self._iterateType(graph, 'ConceptScheme'):
            uri = normalise_uri(subject)
            # create the basic concept
            title = str(self._valueFromPredicates(graph, subject, pred_titles))
            description = str(
                self._valueFromPredicates(graph, subject, pred_descriptions))
            debug('creating ConceptScheme %s', uri)
            cache[uri] = ConceptScheme(uri, title, description)
            schemes.add(uri)

        return schemes

    def load(self, graph, lang='en'):
        cache = {}
        normalise_uri = self.normalise_uri
        self._concepts = set((normalise_uri(subj) for subj in
                              self._iterateType(graph, 'Concept')))
        self._collections = set((normalise_uri(subj) for subj in
                                 self._iterateType(graph, 'Collection')))
        self._schemes = set((normalise_uri(subj) for subj in
                             self._iterateType(graph, 'ConceptScheme')))
        self._resolveGraph(graph)
        self._flat_concepts = self._loadConcepts(graph, cache, lang)
        self._flat_collections = self._loadCollections(graph, cache)
        self._flat_schemes = self._loadConceptSchemes(graph, cache)
        self._flat_cache = cache  # all objects
        self._cache = dict((uri, cache[uri]) for uri in (
            chain(self._concepts, self._schemes, self._collections)))

    def _getAttr(self, name, flat=None):
        if flat is None:
            flat = self.flat
        if flat:
            name = '_flat%s' % name
        return getattr(self, name)

    def _getCache(self, flat=None):
        return self._getAttr('_cache', flat)

    # Implement the interface for `collections.Iterable`
    def __iter__(self, flat=None):
        return iter(self._getCache(flat))

    # Implement the interface for `collections.Container`
    def __contains__(self, value, flat=None):
        return value in self._getCache(flat)

    # Implement the interface for `collections.Sized`
    def __len__(self, flat=None):
        return len(self._getCache(flat))

    # Implement the interface for `collections.Mapping`
    def __getitem__(self, key):
        # try and return a cached item
        return self._getCache()[key]

    def getConcepts(self, flat=None):
        cache = self._getCache(flat)
        concepts = self._getAttr('_concepts', flat)

        return Concepts([cache[key] for key in concepts])

    def getConceptSchemes(self, flat=None):
        cache = self._getCache(flat)
        schemes = self._getAttr('_schemes', flat)

        return Concepts([cache[key] for key in schemes])

    def getCollections(self, flat=None):
        cache = self._getCache(flat)
        collections = self._getAttr('_collections', flat)

        return Concepts([cache[key] for key in collections])


class RDFBuilder(object):
    """
    Creates a RDF graph from Python SKOS objects

    The primary method of this class is `build()`.

    Use the `RDFLoader` class to convert the RDF graph back into the
    Python SKOS object model.
    """

    def __init__(self):
        self.SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        self.DC = rdflib.Namespace("http://purl.org/dc/elements/1.1/")

    def getGraph(self):
        # Instantiate the graph
        graph = rdflib.Graph()

        # Bind a few prefix, namespace pairs.
        graph.bind("dc", "http://purl.org/dc/elements/1.1/")
        graph.bind("skos", "http://www.w3.org/2004/02/skos/core#")
        return graph

    def objectInGraph(self, obj, graph):
        return (rdflib.term.URIRef(obj.uri), rdflib.term.URIRef(
            u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                rdflib.term.URIRef(
                    u'http://www.w3.org/2004/02/skos/core#%s' % obj.__class__.__name__)) in graph

    def buildConcept(self, graph, concept):
        """
        Add a `skos.Concept` instance to a RDF graph
        """
        if self.objectInGraph(concept, graph):
            return

        node = rdflib.URIRef(concept.uri)
        graph.add((node, rdflib.RDF.type, self.SKOS['Concept']))
        graph.add(
            (node, self.SKOS['notation'], rdflib.Literal(concept.notation)))
        graph.add(
            (node, self.SKOS['prefLabel'], rdflib.Literal(concept.prefLabel)))
        graph.add((node, self.SKOS['definition'],
                   rdflib.Literal(concept.definition)))
        graph.add(
            (node, self.SKOS['altLabel'], rdflib.Literal(concept.altLabel)))

        for uri, synonym in concept.synonyms.items():
            graph.add((node, self.SKOS['exactMatch'], rdflib.URIRef(uri)))
            self.buildConcept(graph, synonym)

        for uri, related in concept.related.items():
            graph.add((node, self.SKOS['related'], rdflib.URIRef(uri)))
            self.buildConcept(graph, related)

        for uri, broader in concept.broader.items():
            graph.add((node, self.SKOS['broader'], rdflib.URIRef(uri)))
            self.buildConcept(graph, broader)

        for uri, narrower in concept.narrower.items():
            graph.add((node, self.SKOS['narrower'], rdflib.URIRef(uri)))
            self.buildConcept(graph, narrower)

        for collection in concept.collections.values():
            self.buildCollection(graph, collection)

    def buildCollection(self, graph, collection):
        """
        Add a `skos.Collection` instance to a RDF graph
        """
        if self.objectInGraph(collection, graph):
            return

        node = rdflib.URIRef(collection.uri)
        graph.add((node, rdflib.RDF.type, self.SKOS['Collection']))
        graph.add((node, self.DC['title'], rdflib.Literal(collection.title)))
        graph.add((node, self.DC['description'],
                   rdflib.Literal(collection.description)))
        try:
            date = collection.date.isoformat()
        except AttributeError:
            pass
        else:
            graph.add((node, self.DC['date'], rdflib.Literal(date)))

        for uri, member in collection.members.items():
            graph.add((node, self.SKOS['member'], rdflib.URIRef(uri)))
            self.buildConcept(graph, member)

    def build(self, objects, graph=None):
        """
        Create an RDF graph from Python SKOS objects

        `objects` is an iterable of any instances which are members of
        the Python SKOS object model.  If `graph` is provided the
        objects are added to the graph rather than creating a new
        `Graph` instance.  An empty graph can be created with the
        `getGraph` method.
        """
        if graph is None:
            graph = self.getGraph()

        for obj in objects:
            try:
                obj.prefLabel
            except AttributeError:
                self.buildCollection(graph, obj)
            else:
                self.buildConcept(graph, obj)

        return graph
