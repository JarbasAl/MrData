DEFINED_BY = "<http://www.xxx.nop/mrdata-syntax#>"
import types


class MrDataThing(object):
    uri = "mrdata:thing"
    class_properties = []

    def __init__(self, uri=None, properties=None):
        self._properties = self.class_properties.copy()
        uri = uri or self.__class__.__name__

        assert isinstance(uri, str)
        if ":" in uri:
            uri = uri.split(":")[-1]
        if uri == self.__class__.__name__:
            self.uri = "mrdata:" + uri
        else:
            self.uri = "mrdata_ex:" + uri
        properties = properties or []
        for prop in properties:
            self.add_property(prop)

    def add_property(self, prop):
        assert isinstance(prop, MrDataProperty)
        new_class_uri = prop.__class__.uri.split(":")[-1] + ":" + \
                        prop._target.__class__.__name__
        thingClass = types.new_class(new_class_uri.replace(":", "_"),
                                     (prop.__class__,))

        thingClass.uri = new_class_uri
        if isinstance(prop, UniqueProperty):
            for p in self.class_properties:
                if p.uri == prop.uri:
                    # TODO log error
                    return
            for idx, p in enumerate(self._properties):
                if p.uri.split(":")[-1] == prop.uri.split(":")[-1]:
                    self._properties[idx] = prop
                    return
        prop.uri = self.uri.split(":")[-1] + ":" + prop.uri.split(":")[-1]
        prop._source = self
        prop.__class__ = thingClass
        self._properties.append(prop)

    @property
    def has_for_property(self):
        return self._properties

    def __repr__(self):
        return self.uri

    def as_triples(self):
        triples = self.as_rdf_triples()
        for prop in self.has_for_property:
            for p in prop.as_triples():
                if p not in triples:
                    triples.append(p)
            triples.append((self.uri, "mrdata:has_property", prop.uri))
        return triples

    def as_rdf_triples(self):
        triples = []
        if self.uri != self.__class__.uri:
            triples.append((self.uri, "rdf:type", self.__class__.uri))
        return triples

    def as_owl_triples(self):
        triples = []

        return triples

    def as_skos_triples(self):
        triples = []

        return triples

    def as_standard_format(self):
        return [self]

    def as_sql(self, include_props=True):
        from mister_data.data_models.sql import MrDataSQLProperty, \
            MrDataSQLThing, MrDataSQLConnection
        parent, uri = self.uri.split(":")
        thing = MrDataSQLThing(uri=uri)
        if include_props:
            for prop in self.has_for_property:
                p = prop.as_sql()
                thing.properties += [p]
        return thing


class MrDataProperty(MrDataThing):
    uri = "mrdata:property"

    def __init__(self, target_object=None, source_object=None,
                 properties=None):
        MrDataThing.__init__(self, self.__class__.__name__, properties)

        if source_object is not None:
            assert isinstance(source_object, MrDataThing)
            source_object.add_property(self)
        self._source = source_object
        self._target = target_object
        if hasattr(target_object, "uri"):
            self.uri = self.uri.split(":")[-1] + ":" + \
                       target_object.uri.split(":")[-1]
        else:
            self.uri = "mrdata_prop:" + self.__class__.__name__

    def as_triples(self):
        triples = self.as_rdf_triples()
        for prop in self.has_for_property:
            for p in prop.as_triples():
                if p not in triples:
                    triples.append(p)
            triples.append((self.uri, "mrdata:has_property", prop.uri))

        if isinstance(self.has_value, MrDataThing):
            for p in self.has_value.as_triples():
                if p not in triples:
                    triples.append(p)
        if hasattr(self.has_value, "uri"):
            triples += [
                (self.uri, "mrdata:has_value", self.has_value.uri)
            ]
        else:
            triples += [
                (self.uri, "mrdata:has_value", self.has_value)
            ]
        return triples

    def as_rdf_triples(self):
        triples = []
        if self.uri != self.__class__.uri:
           triples.append((self.uri, "rdf:type", self.__class__.uri))
        return triples

    @property
    def is_subproperty(self):
        return isinstance(self._source, MrDataProperty)

    @property
    def is_literal(self):
        return not hasattr(self._target, "uri")

    @property
    def property_of(self):
        return self._source

    @property
    def has_value(self):
        return self._target

    def __repr__(self):
        return self.uri

    def as_sql(self, include_thing=True):
        from mister_data.data_models.sql import MrDataSQLProperty, \
            MrDataSQLThing, MrDataSQLConnection
        parent, uri = self.uri.split(":")
        if self.is_literal:
            thing = MrDataSQLProperty(uri=uri, value=self.has_value,
                                      parent=self.__class__.__name__)

            if self.property_of and include_thing:
                thing.thing = self.property_of.as_sql(False)
        else:
            if isinstance(self.has_value, MrDataThing):
                # instance
                value = self.has_value.as_sql()
            else:
                # class
                value = self.has_value(
                    self.has_value.__name__).as_sql()
            thing = MrDataSQLConnection(uri=parent,
                                        value=value)

        return thing


class UniqueProperty(MrDataProperty):
    uri = "mrdata:unique_property"
