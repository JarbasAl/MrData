from mister_data.data_models.owl import MrDataOwlThing, MrDataOwlProperty
from mister_data.data_models import MrDataThing, MrDataProperty
from mister_data.data_models.sql import MrDataSQLThing


class Animal(MrDataOwlThing):
    pass


class Dog(Animal):
    pass


class Labrador(Dog):
    pass


class Cat(Animal):
    pass


# Define properties with domain and range
class has_name(MrDataOwlThing >> str):
    pass


class has_age(MrDataOwlThing >> int):
    pass


class related_to_this(MrDataOwlThing >> MrDataOwlThing):
    pass


# NOTE you need to use has_for_property
# default owlready properties are not MrDataOwlProperty by default

assert not isinstance(has_age, MrDataOwlProperty)

dog = Dog("my_dog")
dog.has_name = "jurebes"
dog.has_age = 10
dog.related_to_this = [Cat("rex"), Cat]

from pprint import pprint

# retrieve properties
for p in dog.has_for_property:
    assert p.property_of == dog
    print(p.name, p.has_value)
    pprint(p.as_triples())
    assert isinstance(p, MrDataOwlProperty)

    # in standard format lists need more than one prop!
    for prop in p.as_standard_format():
        assert isinstance(prop, MrDataProperty)
    """
    my_dog:related_to_this [mrdata.rex, mrdata.Cat]
    [('my_dog:related_to_this', 'rdf:type', 'mrdata_prop:related_to_this'),
     ('mrdata_ex:rex', 'rdf:type', 'mrdata:Cat'),
     ('my_dog:related_to_this', 'mrdata:has_value', 'mrdata_ex:rex'),
     ('my_dog:related_to_this', 'mrdata:has_value', 'mrdata:Cat')]
    
    my_dog:has_name jurebes
    [('my_dog:has_name', 'rdf:type', 'mrdata_prop:has_name'),
     ('my_dog:has_name', 'mrdata:has_value', 'jurebes')]
    
    my_dog:is_a [mrdata.Dog]
    [('my_dog:is_a', 'rdf:type', 'mrdata_prop:is_a'),
     ('my_dog:is_a', 'mrdata:has_value', 'mrdata:Dog')]
    
    my_dog:has_age 10
    [('my_dog:has_age', 'rdf:type', 'mrdata_prop:has_age'),
     ('my_dog:has_age', 'mrdata:has_value', 10)]
    """

pprint(dog.as_standard_format().as_triples())

"""
[('mrdata_ex:my_dog', 'rdf:type', 'mrdata:Dog'),
 ('my_dog:related_to_this', 'rdf:type', 'mrdata:property'),
 ('mrdata_ex:rex', 'rdf:type', 'mrdata:Cat'),
 ('my_dog:related_to_this', 'mrdata:has_value', 'mrdata_ex:rex'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'my_dog:related_to_this'),
 ('my_dog:related_to_this', 'mrdata:has_value', 'mrdata:Cat'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'my_dog:related_to_this'),
 ('my_dog:has_name', 'rdf:type', 'mrdata:property'),
 ('my_dog:has_name', 'mrdata:has_value', 'jurebes'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'my_dog:has_name'),
 ('my_dog:has_age', 'rdf:type', 'mrdata:property'),
 ('my_dog:has_age', 'mrdata:has_value', 10),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'my_dog:has_age')]
"""

# get related knowledge from ontology

print(dog.is_a)  # [mrdata.Dog]
print(
    Dog.ancestors())  # {mrdata.Animal, mrdata.MrDataOwlThing, mrdata.Dog, owl.Thing}
print(Animal.instances())  # [mrdata.my_dog, mrdata.rex]
print(
    Animal.descendants())  # {mrdata.Cat, mrdata.Animal, mrdata.Labrador, mrdata.Dog}

pprint(dog.deduced_triples())

"""
[('my_dog:is_a', 'rdf:type', 'mrdata:property'),
 ('my_dog:is_a', 'mrdata:has_value', 'mrdata:Dog'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'my_dog:is_a'),
 ('is_a:Animal', 'rdf:type', 'mrdata:property'),
 ('is_a:Animal', 'mrdata:has_value', 'mrdata:Animal'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'is_a:Animal'),
 ('has_for_example:Labrador', 'rdf:type', 'mrdata:property'),
 ('has_for_example:Labrador', 'mrdata:has_value', 'mrdata:Labrador'),
 ('mrdata_ex:my_dog', 'mrdata:has_property', 'has_for_example:Labrador')]
"""

# convert across formats
assert isinstance(dog.as_standard_format(), MrDataThing)
assert isinstance(dog.as_sql(), MrDataSQLThing)
