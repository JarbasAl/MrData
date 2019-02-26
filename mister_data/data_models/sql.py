from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

import types
from mister_data.data_models.memory import MrDataProperty, MrDataThing

Base = declarative_base()


def model_to_dict(obj):
    serialized_data = {c.key: getattr(obj, c.key) for c in
                       obj.__table__.columns}
    return serialized_data


def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


thing_properties = Table('thing_properties', Base.metadata,
                         Column('thing_id', ForeignKey('thing.uri'),
                                primary_key=True),
                         Column('property_id', ForeignKey('property.uri'),
                                primary_key=True)
                         )

thing_connections = Table('thing_connections', Base.metadata,
                          Column('thing_id', ForeignKey('thing.uri'),
                                 primary_key=True),
                          Column('connection_id', ForeignKey('connection.uri'),
                                 primary_key=True)
                          )


class MrDataSQLThing(Base):
    __tablename__ = 'thing'
    uri = Column(String, primary_key=True)

    properties = relationship("MrDataSQLProperty",
                              secondary=thing_properties,
                              back_populates="thing")

    connections = relationship("MrDataSQLConnection",
                               secondary=thing_connections,
                               back_populates="value")
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'thing',
        'polymorphic_on': type
    }

    def __init__(self, uri=None, properties=None, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        uri = uri or self.__class__.__name__
        if not isinstance(uri, str):
            # class passed
            if hasattr(uri, "uri"):
                uri = uri.uri
            else:
                raise ValueError
        if ":" in uri:
            uri = uri.split(":")[-1]
        if uri == self.__class__.__name__:
            self.uri = "mrdata:" + uri
        else:
            self.uri = "mrdata_ex:" + uri

        properties = properties or []
        for prop in properties:
            self.add_property(prop)

    def __repr__(self):
        return self.uri

    def add_property(self, prop):
        assert isinstance(prop, MrDataSQLProperty) or \
               isinstance(prop, MrDataSQLConnection)
        self.properties.append(prop)

    def as_standard_format(self, include_cons=True):
        thingClass = types.new_class(self.__class__.__name__, (MrDataThing,))
        if self.__class__.__name__ == self.uri.split(":")[-1]:
            thingClass.uri = "mrdata:" + self.__class__.__bases__[0].__name__
        else:
            thingClass.uri = "mrdata:" + self.__class__.__name__

        if hasattr(self, "class_properties"):
            for prop in self.class_properties:
                p = prop.as_standard_format()
                thingClass.class_properties.append(p)

        thing = thingClass(self.uri)
        for prop in self.properties:
            p = prop.as_standard_format(include_thing=False)
            p._source = thing
            if isinstance(prop, MrDataSQLConnection):
                # bypass uri mutation
                p.uri = self.uri.split(":")[-1] + ":" + p.uri.split(":")[-1]
                thing._properties.append(p)
            else:
                thing.add_property(p)

        return thing

    def as_sql(self):
        return self

    def as_triples(self):
        return self.as_standard_format().as_triples()


class MrDataSQLProperty(MrDataSQLThing):
    __tablename__ = "property"

    uri = Column(Integer, ForeignKey('thing.uri'), primary_key=True)

    value = Column(String)

    thing = relationship("MrDataSQLThing", back_populates="properties",
                         secondary=thing_properties, uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'property'
    }

    def __init__(self, target_object=None, source_object=None,
                 properties=None, *args, **kwargs):
        MrDataSQLThing.__init__(self, *args, **kwargs)

        # TODO type support
        self.value = target_object

        if hasattr(target_object, "uri"):

            self.uri = self.__class__.__name__ + ":" + \
                       str(target_object.uri).split(":")[-1]
            if isinstance(target_object, MrDataSQLThing):
                target_object.add_property(self)

        else:
            self.uri = "mrdata:" + self.__class__.__name__

        properties = properties or []
        for prop in properties:
            self.add_property(prop)

    def as_standard_format(self, include_thing=True):
        propClass = types.new_class(self.uri, (MrDataProperty,))
        propClass.uri = "mrdata_prop:" + propClass.__name__.split(":")[0]

        prop = propClass(self.value)
        prop.uri = self.uri
        if self.thing:
            if include_thing:
                prop._source = self.thing.as_standard_format()
        for p in self.properties:
            prop.add_property(p.as_standard_format(False))
        return prop


class MrDataSQLConnection(MrDataSQLThing):
    __tablename__ = "connection"

    uri = Column(Integer, ForeignKey('thing.uri'), primary_key=True)

    value = relationship("MrDataSQLThing", back_populates="connections",
                         secondary=thing_connections, uselist=False)

    thing = relationship("MrDataSQLThing", back_populates="properties",
                         secondary=thing_properties, uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'connection',
    }

    def __init__(self, target_object=None, source_object=None,
                 properties=None, *args, **kwargs):
        MrDataSQLThing.__init__(self, *args, **kwargs)

        if target_object is not None:
            if not isinstance(target_object,
                              MrDataSQLThing) and not isinstance(
                    target_object, MrDataSQLConnection) and not isinstance(
                target_object, MrDataSQLProperty):
                # instantiate so we can assign it
                target_object = target_object()

            assert hasattr(target_object, "uri")

            # target_object.add_property(self)

            self.uri = self.__class__.__name__ + ":" + \
                       str(target_object.uri).split(":")[-1]
        else:
            self.uri = "mrdata_prop:" + self.__class__.__name__

        self.value = target_object

        properties = properties or []
        for prop in properties:
            self.add_property(prop)

    def as_standard_format(self, include_thing=True):
        propClass = types.new_class(self.uri, (MrDataProperty,))
        propClass.uri = "mrdata_prop:" + propClass.__name__.split(":")[0]

        prop = propClass()
        prop.uri = self.uri
        if self.thing:
            prop.uri = self.thing.uri.split(":")[-1] + ":" + \
                       prop.uri.split(":")[-1]
            if include_thing:
                prop._source = self.thing.as_standard_format()
        if self.value:
            prop._target = self.value.as_standard_format()
        for p in self.properties:
            prop.add_property(p.as_standard_format(False))
        #print(prop.__dict__)
        return prop
