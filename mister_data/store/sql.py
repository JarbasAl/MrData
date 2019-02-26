from sqlalchemy.ext.declarative import declarative_base
from os.path import join, expanduser, exists
from os import makedirs
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, \
    Table, Float, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import json

from mister_data.data_models.sql import Base, MrDataSQLProperty, \
    MrDataSQLThing, MrDataSQLConnection


class GenericSQLDatabase(object):
    def __init__(self, name, path=None, debug=False, session=None):
        if path is None:
            path = join(expanduser("~"), "mister_data", "sql")
            if not exists(path):
                makedirs(path)
            path = 'sqlite:///' + join(path, name + '.db')
        self.db = create_engine(path)
        self.db.echo = debug

        if session:
            self.session = session
        else:
            Session = sessionmaker(bind=self.db)
            self.session = Session()
        Base.metadata.create_all(self.db)

    # searching
    def query(self, query):
        return self.session.query(query)

    def total_things(self):
        return self.session.query(MrDataSQLThing).count()

    def total_properties(self):
        return self.session.query(MrDataSQLProperty).count()

    def search_by_uri(self, thing_id):
        return self.query(MrDataSQLThing).filter_by(uri=thing_id).one()

    def search_by_property(self, uri):
        things = []
        for prop in self.query(MrDataSQLProperty).filter_by(uri=uri).all():
            things += prop.thing
        return things

    def search_by_value(self, value):
        return self.query(MrDataSQLProperty).filter_by(value=value).all()

    # creation
    def add_thing(self, thing, properties=None):
        if isinstance(thing, MrDataSQLThing):
            self.session.add(thing)
        if isinstance(thing, str):
            try:
                thing = json.loads(thing)
            except:
                thing = MrDataSQLThing(uri=thing)
                self.session.add(thing)
        if isinstance(thing, dict):
            thing = self.add_thing_from_json(thing)

        properties = properties or []

        if isinstance(thing, MrDataSQLThing):
            for prop in properties:
                p = self.add_property(prop)
                thing.properties += [p]
            return thing
        else:
            raise ValueError

    def add_property(self, prop, value=None):
        if isinstance(prop, MrDataSQLProperty):
            self.session.add(prop)
        if isinstance(prop, str):
            try:
                prop = json.loads(prop)
            except:
                prop = MrDataSQLProperty(uri = prop)
                self.session.add(prop)
        if isinstance(prop, dict):
            prop = self.add_property_from_json(prop)
        if isinstance(prop, tuple) or isinstance(prop, list):
            assert len(prop) == 2
            new_id = self.total_things() + 1
            prop = MrDataSQLProperty(uri=prop[0], value=prop[1])
            self.session.add(prop)

        if isinstance(prop, MrDataSQLProperty):
            if value:
                prop.value = value
            return prop
        else:
            raise ValueError

    def add_property_from_json(self, prop_json):

        if isinstance(prop_json, str):
            prop_json = json.loads(prop_json)

        assert isinstance(prop_json, dict)
        name = prop_json["uri"]
        value = prop_json.get("value")
        props = prop_json.get("properties", [])

        prop = MrDataSQLProperty(uri=name)
        if value:
            prop.value = value
        for p in props:
            p = self.add_property_from_json(p)
            prop.properties.append(p)
        self.session.add(prop)
        return prop

    def add_thing_from_json(self, thing_json):

        if isinstance(thing_json, str):
            thing_json = json.loads(thing_json)

        assert isinstance(thing_json, dict)
        name = thing_json["uri"]
        props = thing_json.get("properties", [])

        thing = MrDataSQLThing(uri=name)
        for prop in props:
            p = self.add_property(prop)
            thing.properties += [p]
        self.session.add(thing)
        return thing

    # session
    def commit(self):
        try:
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
        return False

    def close(self):
        self.session.close()

    def __enter__(self):
        """ Context handler """
        if self.session:
            self.close()
            self.session = None
        Session = sessionmaker(bind=self.db)
        self.session = Session()
        return self

    def __exit__(self, _type, value, traceback):
        """ Commits changes and Closes the session """
        self.commit()
        self.close()



def test_db():
    with GenericSQLDatabase("my_db") as db:
        # inspect
        thing = db.add_thing("my_thing")
        print(thing.name)
        print(thing.type)
        thing.description = "thing number 0"
        print(thing.description)
        print(thing.as_json())
        print(db.search_by_name("my_thing")[0].as_json())
        print(db.search_by_type("thing")[0].name)
        property = db.add_property("color", value="red")
        print(db.search_by_type("property")[0].as_json())
        print(db.search_by_type("property")[0].things)

        thing.properties.append(property)
        print(property.things[0].as_json())
        print(db.search_by_type("property")[0].things)
        print(property.type)
        assert isinstance(property, MrDataSQLThing)
        print(property.as_json())
        print(thing.name, thing.properties[0].name, thing.properties[0].value)
        print(db.total_things())
        print(db.search_by_property("color")[0].name)
        print(db.search_by_value("red")[0].name)
        print(db.search_by_value("red")[0].type)
        print(db.search_by_name("my_thing")[0].name, db.search_by_name(
            "my_thing")[0].type)
        print(db.search_by_name("color")[0].value, db.search_by_name(
            "color")[0].type)



if __name__ == "__main__":
    test_db()
