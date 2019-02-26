from mister_data.data_models import MrDataProperty, MrDataThing, UniqueProperty
from pprint import pprint

thing = MrDataThing("MrDataSQLThing#1")
print(thing.has_for_property)  # list of properties

prop = MrDataProperty("some value")
print(prop.property_of)  # None / not assigned
print(prop.has_value)  # "some value"


class Is_A(MrDataProperty):
    uri = "mrdata_prop:Is_A"


class Age(UniqueProperty):
    uri = "mrdata_prop:Age"


class Animal(MrDataThing):
    uri = "mrdata:Animal"


class FourLeggedThing(MrDataThing):
    uri = "mrdata:FourLeggedThing"


class Dog(MrDataThing):
    uri = "mrdata:Dog"
    class_properties = [Is_A(Animal)]


class Chicken(MrDataThing):
    uri = "mrdata:Cat"
    class_properties = [Is_A(Animal)]

dog = Animal("dog")
print(Animal.uri)  # class
print(dog.uri)  # individual
print(dog.as_triples())

print(Animal.class_properties)  # no class properties
print(Dog.class_properties[0].as_triples())  # is_a Animal

# Create Individuals
dog = Dog("jurebes")

print(Animal.uri)  # class
print(Dog.uri)  # class
print(dog.uri)  # individual

# MrDataSQLProperty classes
print(Is_A.uri)  # mrdata_prop:Is_A
print(Age.has_value)  # <property object at 0xb782402c> / undefined

# MrDataSQLProperty individuals
print(Is_A(Animal).uri)  # mrdata_ex:Is_A"
print(Is_A(Animal).has_value)  # 10, has a value
print(Age(10).property_of)  # None

# assign to individuals
dog.add_property(Age(6))
print(dog.has_for_property)  # is_a Animal, age 6

# assign on property creation
chicken = Chicken("MyChicken")
age = Age(10, chicken)
assert age in chicken.has_for_property
print(age.property_of)  # mrdata_ex:MyCat
try:
    age = Age(10, Chicken)
except AssertionError:
    print("Can't assign to classes, must be declared")

# unique properties are replaced when reassigned
print(chicken.has_for_property)  # 1x age 10
chicken.add_property(Age(6))
print(chicken.has_for_property)  # 1x age 6
age = Age(10, chicken)
print(chicken.has_for_property)  # 1x age 10

print(Chicken.class_properties)
print(chicken.has_for_property)  # 1x age 10

dog.add_property(Is_A(FourLeggedThing))
print(dog.has_for_property)
print(Dog.class_properties)
