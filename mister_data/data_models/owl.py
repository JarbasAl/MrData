from owlready2 import *
import types
from mister_data.data_models import MrDataThing, MrDataProperty
from pprint import pprint

onto = get_ontology("mrdata.owl")

with onto:
    class MrDataOwlThing(Thing):
        uri = "mrdata:thing"

        def __init__(self, name=None, properties=None, ontology=None, **kargs):
            properties = properties or []
            self._properties = []
            for p in properties:
                self.add_property(p)
            Thing.__init__(self, name, ontology, **kargs)
            if name and name != self.__class__.__name__:
                self.uri = "mrdata_ex:" + name
            else:
                self.uri = "mrdata:" + self.__class__.__name__

        def add_property(self, prop):
            assert isinstance(prop, MrDataOwlProperty)
            self._properties.append(prop)

        def as_sql(self):
            return self.as_standard_format().as_sql()

        def as_owl(self):
            return self

        def as_standard_format(self, include_parents=False):
            # create thing object
            thingClass = types.new_class(self.uri.split(":")[-1],
                                         (MrDataThing,))
            if self.uri.split(":")[-1] == self.__class__.__name__:
                thingClass.uri = "mrdata:" + \
                                 self.__class__.__bases__[0].__name__
            else:
                thingClass.uri = "mrdata:" + self.__class__.__name__
            thing = thingClass(self.name)
            thing.uri = self.uri
            if hasattr(self, "has_for_property"):
                for prop in self.has_for_property():
                    prop_class_name = prop.name
                    prop_value = prop.has_value.name

                    if callable(prop.has_value):

                        propClass = types.new_class(prop_class_name,
                                                    (MrDataProperty,))
                        propClass.uri = "mrdata_prop:" + prop_class_name

                        p = propClass()
                        po = prop.has_value().as_standard_format().__class__
                        po.uri = "mrdata:" + prop_value
                        p._target = po
                        p.uri = prop_class_name + ":" + prop_value
                        thing._properties.append(p)
                    else:
                        inst = prop.uri.split(":")[-1]
                        thingClass = prop.is_a[0]().as_standard_format().__class__
                        thingClass.uri = "mrdata:" + thingClass.__name__
                        po = prop.is_a[1]().as_standard_format()
                        po.uri = self.name + ":" + inst
                        po.__class__.uri = po.__class__.__name__ + ":" + \
                                           thingClass.__name__
                        po._target = thingClass(inst)
                        thing._properties.append(po)
            else:
                #pprint(self.__class__().has_for_property)
                if hasattr(self.__class__, "class_properties"):
                    for prop in self.__class__.class_properties:
                        prop_class_name = prop.name
                        prop_value = prop.has_value.name

                        if callable(prop.has_value):
                            propClass = types.new_class(prop_class_name,
                                                        (MrDataProperty,))
                            propClass.uri = "mrdata_prop:" + prop_class_name

                            p = propClass()
                            po = prop.has_value().as_standard_format().__class__
                            po.uri = "mrdata:" + prop_value
                            p._target = po
                            p.uri = prop_class_name + ":" + prop_value
                            thing._properties.append(p)
                        else:
                            thingClass = prop.is_a[0]().as_standard_format().__class__
                            thingClass.uri = "mrdata:" + thingClass.__name__
                            po = prop.is_a[1]().as_standard_format()
                            po.uri = po.__class__.__name__ + ":" + \
                                     thingClass.__name__
                            po.__class__.uri = "mrdata_prop:" + \
                                               po.__class__.__name__
                            po._target = thingClass
                            thing._properties.append(po)

            return thing

        def as_standard_format_expanded(self):
            thing = self.as_standard_format(True)
            for ance in self.__class__.ancestors():
                if ance.__name__ in ["Thing", "MrDataOwlThing",
                                     self.__class__.__name__]:
                    continue
                inst = ance().as_standard_format().__class__
                propClass = types.new_class("is_a", (MrDataProperty,))
                prop = propClass(inst)
                prop._target = inst
                thing._properties += [prop]
            for ance in self.__class__.descendants():
                if ance.__name__ in ["Thing", "MrDataOwlThing",
                                     self.__class__.__name__]:
                    continue
                inst = ance().as_standard_format().__class__
                propClass = types.new_class("has_for_example",
                                            (MrDataProperty,))
                prop = propClass(inst)
                prop._target = inst
                thing._properties += [prop]

            return thing

        def deduced_triples(self):
            triples = self.as_triples()
            all = self.as_standard_format_expanded().as_triples()
            return [t for t in all if t not in triples]

        def as_triples(self):
            std = self.as_standard_format()
            triples = []
            bucket = []
            if isinstance(std, list):
                for a in std:
                    bucket += a.as_triples()
            else:
                bucket = std.as_triples()
            for t in bucket:
                if t not in triples:
                    triples += [t]
            return triples

        def has_for_property(self):
            as_dict = self.__dict__
            if hasattr(self.__class__, "class_properties"):
                props = self.__class__.class_properties
            else:
                props = []
            for k in as_dict:
                if k in ["storid", "namespace"]:
                    continue
                if k.startswith("_"):
                    continue
                continue # TODO
                propClass = types.new_class(k, (MrDataOwlProperty,))

                prop = propClass(self.name + ":" + k)
                prop.has_value = as_dict[k]
                prop.property_of = self
                props.append(prop)
            return props + self._properties


    class MrDataOwlProperty(MrDataOwlThing):
        uri = "mrdata:property"
        has_value = None
        property_of = None

        def __init__(self, target_object=None, source_object=None,
                     properties=None, ontology=None, **kargs):
            if target_object:
                p = target_object.__class__.__bases__[-1].__name__
                t = target_object.name
                self._target_dict = target_object.__dict__
            MrDataOwlThing.__init__(self, self.__class__.__name__,
                                    properties, ontology, **kargs)

            if target_object is None:
                self.uri = "mrdata_prop:" + self.__class__.__name__
            else:
                assert hasattr(target_object, "uri")
                self.uri = p + ":" + t
            self.has_value = target_object

        def as_standard_format(self):

            # create prop object
            #print(self.is_a)
            propClass = types.new_class(self.uri.split(":")[-1],
                                        (MrDataProperty,))
            propClass.uri = "mrdata_prop:" + self.uri.split(":")[0]
            prop = propClass(self.name)
            prop.uri = self.uri

            if hasattr(self, "has_for_property"):
                for prop in self.has_for_property():
                    print(prop.as_triples())

            if isinstance(self.has_value, list):
                # TODO
                print(1, self.__class__)
            else:
                if not callable(self.has_value):
                    # individual
                    thingClass = types.new_class(self.is_a[0].name,
                                                 (MrDataThing,))
                    thingClass.uri = "mrdata:" + self.is_a[0].name
                    thing = thingClass()
                    thing.uri = "mrdata_ex:" + self.uri.split(":")[-1]

                    prop._target = thing
                else:
                    # class
                    # TODO
                    print(3, self.has_value.__class__)

            return prop

if __name__ == "__main__":
    from pprint import pprint

    pprint(onto.get_triples(None, None, None))
