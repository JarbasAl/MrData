from mister_data.data_models.sql import MrDataSQLConnection, MrDataSQLThing, MrDataSQLProperty
from pprint import pprint

thing = MrDataSQLThing(uri="Dog", uri="jurebes")

print(thing.uri)
print(thing.parent)
print(thing.type)

prop = MrDataSQLProperty(uri="name", value="jurebes")
print(prop.uri)
print(prop.value)
assert isinstance(prop, MrDataSQLThing)
print(thing.properties)
thing.properties.append(prop)
print(thing.properties)
print(prop.thing.uri)

standard_thing = thing.as_standard_format()
standard_prop = prop.as_standard_format()

pprint(standard_thing.as_triples())
pprint(standard_prop.as_triples())

print(standard_thing.has_for_property)
print(standard_prop.has_value)
print(standard_prop.property_of)
print(standard_thing.has_for_property[0].property_of)

animal = MrDataSQLThing(uri="Animal")

con = MrDataSQLConnection(uri="is_a", value=animal)
con.thing = thing
pprint(thing.as_triples())

pprint(con.as_triples())

print(animal.type, prop.type, con.type)
print(thing.properties)

for c in animal.connections:
    print(c.thing, c.uri, animal.uri)