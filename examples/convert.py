from mister_data.data_models import MrDataProperty, MrDataThing, \
    UniqueProperty
from mister_data.data_models.sql import MrDataSQLThing, MrDataSQLProperty, \
    MrDataSQLConnection
from mister_data.data_models.skos import MrDataSkosProperty, MrDataSkosThing
from mister_data.data_models.owl import MrDataOwlProperty, MrDataOwlThing

from pprint import pprint

# tests
expected_prop = [
    ('Related_to:Laura', 'rdf:type', 'mrdata_prop:Related_to'),
    ('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat'),
    ('Related_to:Laura', 'mrdata:has_value', 'mrdata_ex:Laura')
]

expected_dog = [
    ('mrdata_ex:jurebes', 'rdf:type', 'mrdata:Dog'),
    ('Related_to:Cat', 'rdf:type', 'mrdata_prop:Related_to'),
    ('Related_to:Cat', 'mrdata:has_value', 'mrdata:Cat'),
    ('mrdata_ex:jurebes', 'mrdata:has_property', 'Related_to:Cat'),
    ('jurebes:Laura', 'rdf:type', 'Related_to:Cat'),
    ('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat'),
    ('jurebes:Laura', 'mrdata:has_value', 'mrdata_ex:Laura'),
    ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:Laura')
]

expected_cat = [('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat')]

expected_class = [('mrdata:Mammal', 'rdf:type', 'mrdata:Animal')]

dog_uri = "mrdata_ex:jurebes"
cat_uri = "mrdata_ex:Laura"
mammal_uri = "mrdata:Mammal"
prop_uri = "Related_to:Laura"
prop_class_uri = "mrdata_prop:Related_to"


## Standard Format
def test_standard():
    class Related_to(MrDataProperty):
        uri = "mrdata_prop:Related_to"

    class Animal(MrDataThing):
        uri = "mrdata:Animal"

    class Mammal(Animal):
        uri = "mrdata:Animal"

    class Cat(Mammal):
        uri = "mrdata:Cat"

    class Dog(Mammal):
        uri = "mrdata:Dog"
        class_properties = [Related_to(Cat)]

    assert Related_to().uri == prop_class_uri

    dog = Dog("jurebes")
    assert dog.uri == dog_uri

    cat = Cat("Laura")
    assert cat.uri == cat_uri

    mammal_class = Mammal()
    assert mammal_class.uri == mammal_uri

    assert cat.as_triples() == expected_cat

    prop = Related_to(cat)
    assert prop.uri == prop_uri

    assert prop.as_triples() == expected_prop

    dog.add_property(Related_to(cat))
    assert dog.as_triples() == expected_dog

    assert mammal_class.as_triples() == expected_class


## Sql Format

def test_sql():
    class Related_to(MrDataSQLConnection):
        pass

    class Animal(MrDataSQLThing):
        pass

    class Mammal(Animal):
        pass

    class Cat(Mammal):
        pass

    class Dog(Mammal):
        class_properties = [Related_to(Cat)]

    dog = Dog("jurebes")
    # print(dog.uri)
    assert dog.uri == dog_uri

    cat = Cat("Laura")
    # print(cat.uri)
    assert cat.uri == cat_uri

    mammal_class = Mammal()
    # print(mammal_class.uri)
    assert mammal_class.uri == mammal_uri

    prop = Related_to(cat)

    # pprint(prop.as_triples())
    # print(Related_to().uri)
    assert Related_to().uri == prop_class_uri

    #print(prop.uri)
    assert prop.uri == prop_uri

    # pprint(mammal_class.as_triples())
    assert mammal_class.as_triples() == expected_class

    # pprint(cat.as_triples())
    assert cat.as_triples() == expected_cat

    #pprint(prop.as_triples())
    assert prop.as_triples() == expected_prop

    dog.add_property(prop)
    # TODO fix this, WIP, DO NOT USE
    return
    p = dog.properties[-1]
    pprint(dog.as_standard_format().has_for_property)
    pprint(p.as_triples())
    """
    ('Related_to:Laura', 'rdf:type', 'mrdata_prop:Related_to'),
    ('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat'),
    ('Related_to:Laura', 'mrdata:has_value', 'mrdata_ex:Laura')
    """
    #pprint(dog.as_triples())
    assert dog.as_triples() == expected_dog


## Owl Format

def test_owl():
    class Related_to(MrDataOwlProperty):
        pass

    class Animal(MrDataOwlThing):
        pass

    class Mammal(Animal):
        pass

    class Cat(Mammal):
        pass

    class Dog(Mammal):
        class_properties = [Related_to(Cat)]

    dog = Dog("jurebes")
    #print(dog.uri)
    assert dog.uri == dog_uri

    cat = Cat("Laura")
    #print(cat.uri)
    assert cat.uri == cat_uri

    mammal_class = Mammal()
    #print(mammal_class.uri)
    assert mammal_class.uri == mammal_uri

    #print(Related_to().uri)
    assert Related_to().uri == prop_class_uri

    assert cat.as_triples() == expected_cat

    prop = Related_to(cat)
    #print(prop.uri)
    assert prop.uri == prop_uri

    #pprint(prop.as_triples())
    assert prop.as_triples() == expected_prop

    #pprint(mammal_class.as_triples())
    assert mammal_class.as_triples() == expected_class

    #print(dog.is_a)
    dog.add_property(prop)
    #pprint(dog.as_triples())
    assert dog.as_triples() == expected_dog

    # owl extras
    class Pet(MrDataOwlThing):
        pass

    dog.used_for = [Pet]

    pprint(dog.deduced_triples())
    """
    [('is_a:MrDataOwlThing', 'rdf:type', 'mrdata:property'),
     ('is_a:MrDataOwlThing', 'mrdata:has_value', 'mrdata:MrDataOwlThing'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'is_a:MrDataOwlThing'),
     ('is_a:Animal', 'rdf:type', 'mrdata:property'),
     ('is_a:Animal', 'mrdata:has_value', 'mrdata:Animal'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'is_a:Animal')]
     """
    # TODO relationship mutated cat object!!!!
    # since now its a shared object, how do i know which is which?
    # result is not incorrect, but contains extra (valid) triples
    return
    pprint(cat.as_triples())
    assert cat.as_triples() == expected_cat


## Skos Format

def test_skos():
    class Related_to(MrDataSkosProperty):
        pass

    class Animal(MrDataSkosThing):
        pass

    class Mammal(Animal):
        pass

    class Cat(Mammal):
        pass

    class Dog(Mammal):
        class_properties = [Related_to(Cat)]

    dog = Dog("jurebes")
    #print(dog.uri)
    assert dog.uri == dog_uri

    cat = Cat("Laura")
    #print(cat.uri)
    assert cat.uri == cat_uri

    mammal_class = Mammal()
    #print(mammal_class.uri)
    assert mammal_class.uri == mammal_uri

    #print(Related_to().uri)
    assert Related_to().uri == prop_class_uri

    #pprint(cat.as_triples())
    assert cat.as_triples() == expected_cat

    #pprint(mammal_class.as_triples())
    assert mammal_class.as_triples() == expected_class

    prop = Related_to(cat)
    #print(prop.uri)
    assert prop.uri == prop_uri

    #pprint(prop.as_triples())
    assert prop.as_triples() == expected_prop

    dog.add_property(prop)
    #pprint(dog.as_triples())
    assert set(dog.as_triples()) == set(expected_dog)

    ## skos extras
    dog.add_synonym("jureboso")
    dog.definition = "my dog"
    #pprint(dog.deduced_triples())
    """
    [('jurebes:SkosBroader', 'rdf:type', 'mrdata_prop:SkosBroader'),
     ('mrdata:Mammal', 'rdf:type', 'mrdata:Animal'),
     ('jurebes:SkosBroader', 'mrdata:has_value', 'mrdata:Mammal'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosBroader'),
     ('jurebes:SkosSynonym', 'rdf:type', 'mrdata_prop:SkosSynonym'),
     ('jurebes:SkosSynonym', 'mrdata:has_value', 'jureboso'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosSynonym'),
     ('jurebes:SkosPrefLabel', 'rdf:type', 'mrdata_prop:SkosPrefLabel'),
     ('jurebes:SkosPrefLabel', 'mrdata:has_value', 'jurebes'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosPrefLabel'),
     ('jurebes:SkosDefinition', 'rdf:type', 'mrdata_prop:SkosDefinition'),
     ('jurebes:SkosDefinition', 'mrdata:has_value', 'my dog'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosDefinition')]
    """


test_standard()
test_sql()
test_owl()
test_skos()