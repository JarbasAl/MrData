from mister_data.utils.skos import Concept
from mister_data.data_models import MrDataThing, MrDataProperty
import types


class MrDataSkosThing(Concept):
    _is_thing = True
    class_properties = []

    def __init__(self, uri=None, prefLabel=None, definition=None,
                 notation=None, altLabel=None):
        if uri:
            uri = "mrdata_ex:" + str(uri)
        else:
            uri = "mrdata:" + self.__class__.__name__
        super(MrDataSkosThing, self).__init__(uri, prefLabel, definition,
                                              notation, altLabel)
        for thing in self.__class__.__bases__:
            if hasattr(thing, "_is_thing") and thing._is_thing:
                t =thing()
                self.broader.add(t)

        for prop in self.class_properties:
            self.add_property(prop)

    @property
    def has_for_property(self):
        props = []
        for thing in self.related:
            prop = self.related[thing]
            if isinstance(prop, MrDataSkosProperty):
                props += [prop]
            else:
                prop = SkosRelated()
                prop.uri = "mrdata_prop:" + thing
                props += [prop]
        for thing in self.broader:
            thing = self.broader[thing]
            prop = SkosBroader(thing)
            props += [prop]
        for thing in self.synonyms:
            thing = self.synonyms[thing]
            prop = SkosSynonym(thing)
            props += [prop]
        if self.prefLabel:
            prop = SkosPrefLabel(self.prefLabel.split(":")[-1])
            props += [prop]
        if self.definition:
            prop = SkosDefinition(self.definition)
            props += [prop]
        return props

    def add_synonym(self, synonym):
        assert isinstance(synonym, str)
        syn = Concept(synonym)
        self.synonyms.add(syn)

    def add_property(self, prop):
        assert isinstance(prop, MrDataSkosProperty)
        self.related.add(prop)

    def add_related(self, thing):
        assert isinstance(thing, MrDataSkosThing)
        self.related.add(thing)

    def as_triples(self):
        triples = []
        for t in self.as_standard_format().as_triples():
            if t not in triples:
                triples.append(t)
        return triples

    def as_standard_format(self):
        thingClass = types.new_class(self.uri, (MrDataThing,))
        thingClass.uri = "mrdata:" + self.__class__.__name__
        if self.uri == thingClass.uri:
            thingClass.uri = "mrdata:" + self.__class__.__bases__[-1].__name__

        thing = thingClass()
        thing.uri = self.uri
        for prop in self.has_for_property:
            if prop.__class__.__name__.startswith("Skos"):
                continue

            if callable(prop._target):
                p = prop.as_standard_format()
            else:
                p2 = prop._target.as_standard_format()
                propClass = types.new_class(self.uri, (MrDataProperty,))
                propClass.uri = prop.uri.split(":")[0] + ":" + \
                                prop._target.__class__.__name__
                p = propClass(p2)
                p.uri = self.uri.split(":")[-1] + ":" + \
                                prop.uri.split(":")[-1]

            thing._properties.append(p)
        return thing

    def as_standard_format_expanded(self):
        thingClass = types.new_class(self.uri, (MrDataThing,))
        thingClass.uri = "mrdata:" + self.__class__.__name__
        if self.uri == thingClass.uri:
            thingClass.uri = "mrdata:" + self.__class__.__bases__[-1].__name__

        thing = thingClass()
        thing.uri = self.uri
        for prop in self.has_for_property:
            if callable(prop._target):
                p = prop.as_standard_format()
            else:
                propClass = types.new_class(self.uri, (MrDataProperty,))
                if prop.uri.split(":")[-1].startswith("Skos"):
                    propClass.uri = prop.uri
                else:
                    propClass.uri = prop.uri.split(":")[0] + ":" + \
                                prop._target.__class__.__name__
                if not hasattr(prop._target, "as_standard_format"):
                    p = propClass(prop._target)

                else:
                    p2 = prop._target.as_standard_format()
                    p = propClass(p2)
                p.uri = self.uri.split(":")[-1] + ":" + \
                        prop.uri.split(":")[-1]

            thing._properties.append(p)
        return thing

    def deduced_triples(self):
        triples = self.as_triples()
        all = self.as_standard_format_expanded().as_triples()
        return [t for t in all if t not in triples]


class MrDataSkosProperty(MrDataSkosThing):
    _target = None

    def __init__(self, target_object=None, source_object=None,
                 properties=None, prefLabel=None, definition=None,
                 notation=None, altLabel=None):
        super(MrDataSkosProperty, self).__init__(None, prefLabel,
                                                     definition,
                                              notation, altLabel)
        if target_object:
            if hasattr(target_object, "uri"):
                if callable(target_object):
                    self.uri = self.__class__.__name__ + ":" + \
                               target_object.__name__
                else:
                    self.uri = self.__class__.__name__ + ":" + \
                               str(target_object.uri).split(":")[-1]
            else:
                self.uri = self.__class__.__name__ + ":" + \
                           target_object.__class__.__name__
            self._target = target_object
        else:
            self.uri = "mrdata_prop:" + self.__class__.__name__

    def as_standard_format(self):
        thingClass = types.new_class(self.uri, (MrDataProperty,))
        thingClass.uri = "mrdata_prop:" + self.uri.split(":")[0]
        thing = thingClass()
        if self._target:
            if callable(self._target):
                inst = self._target().as_standard_format().__class__
                inst.uri = inst.__name__
                thing._target = inst
            else:
                thing._target = self._target.as_standard_format()

        thing.uri = self.uri
        for prop in self.has_for_property:
            if prop.__class__.__name__.startswith("Skos"):
                continue

            thing.add_property(
                prop.as_standard_format())
        return thing

    def as_standard_format_expanded(self, include_props=True):
        thingClass = types.new_class(self.uri, (MrDataProperty,))
        thingClass.uri = "mrdata_prop:" + self.__class__.__name__
        thing = thingClass(self.uri)
        thing.uri = self.__class__.__name__ + ":" + self.uri
        if include_props:
            for prop in self.has_for_property:
                p = prop.as_standard_format_expanded(False)
                if prop.__class__.__name__.startswith("Skos"):
                    # skip uri mutation
                    thing._properties.append(p)
                else:
                    thing.add_property(p)
        return thing


class SkosBroader(MrDataSkosProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = "mrdata_prop:" + self.__class__.__name__


class SkosPrefLabel(MrDataSkosProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = "mrdata_prop:" + self.__class__.__name__


class SkosSynonym(MrDataSkosProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = "mrdata_prop:" + self.__class__.__name__


class SkosDefinition(MrDataSkosProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = "mrdata_prop:" + self.__class__.__name__


class SkosRelated(MrDataSkosProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = "mrdata_prop:" + self.__class__.__name__


if __name__ == "__main__":
    from pprint import pprint

    thing = MrDataSkosThing(uri="dog")
    prop = MrDataSkosProperty(uri="is_a_animal")


    class Animal(MrDataSkosThing):
        pass


    class Is_Alive(MrDataSkosProperty):
        pass


    class Is_A(MrDataSkosProperty):
        pass


    class Mammal(Animal):
        pass  # class_properties = [Is_A("Mammal")]


    class Dog(Mammal):
        pass  # class_properties = [Is_A("Mammal")]

    class Cat(Mammal):
        pass  # class_properties = [Is_A("Mammal")]

    dog_class = Dog()
    # pprint(dog_class.as_triples())
    """
    [('mrdata_ex:Dog', 'rdf:type', 'mrdata:Dog'),
     ('Dog:SkosBroader', 'rdf:type', 'mrdata_prop:SkosBroader'),
     ('Dog:SkosBroader', 'mrdata:has_value', 'SkosBroader:Animal'),
     ('mrdata_ex:Dog', 'mrdata:has_property', 'Dog:SkosBroader')]
    """

    dog_instance = Dog("jurebes")
    dog_instance.add_synonym("jurebeiro")
    dog_instance.add_related(Cat("laura"))

    """
    [('mrdata_ex:jurebes', 'rdf:type', 'mrdata:Dog'),
     ('jurebes:SkosBroader', 'rdf:type', 'mrdata_prop:SkosBroader'),
     ('jurebes:SkosBroader', 'mrdata:has_value', 'SkosBroader:Animal'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosBroader'),
     ('jurebes:SkosSynonym', 'rdf:type', 'mrdata_prop:SkosSynonym'),
     ('jurebes:SkosSynonym', 'mrdata:has_value', 'SkosSynonym:jurebeiro'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosSynonym')]
    """

    prop = Is_A("pet")
    pprint(prop.as_triples())
    pprint(prop.deduced_triples())

    dog_instance.add_property(prop)

    pprint(dog_instance.as_triples())
    pprint(dog_instance.deduced_triples())
