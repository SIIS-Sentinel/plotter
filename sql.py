from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from typing import Any


Base = declarative_base()  # type: Any
hub_ip = "130.203.33.156"
# db_path = "postgresql://pi:password@%s/watchtower" % hub_ip
db_path = "sqlite:///test_db.db"


class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    events = relationship("Event", back_populates="node")
    sensors = relationship("Sensor", back_populates="node")
    measurements = relationship("Measurement", back_populates="node")
    attacks = relationship("Attack", back_populates="node")

    def __repr__(self):
        return "Node(%s)" % (self.name)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    timestamp = Column(Float, index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="events")

    def __repr__(self):
        return "Event(%s, %s, %0.1f)" % (self.node, self.event_type, self.timestamp)


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    unit = Column(String)
    average = Column(Float)
    std = Column(Float)
    node_id = Column(Integer, ForeignKey('nodes.id'), index=True)
    node = relationship("Node", back_populates="sensors")
    measurements = relationship("Measurement", back_populates="sensor")

    def __repr__(self):
        return "Sensor(%s, %s, %s, %0.2f, %0.2f)" % (self.node, self.name, self.unit, self.average, self.std)


class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float, index=True)
    value = Column(Float)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), index=True)
    sensor = relationship("Sensor", back_populates="measurements")
    node_id = Column(Integer, ForeignKey('nodes.id'), index=True)
    node = relationship("Node", back_populates="measurements")

    def __repr__(self):
        return "Measurement(%s, %s, %0.1f, %f)" % (self.node.name, self.sensor.name, self.timestamp, self.value)


class Attack(Base):
    __tablename__ = "attacks"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    attack_type = Column(Integer)
    node_id = Column(Integer, ForeignKey('nodes.id'), index=True)
    node = relationship("Node", back_populates="attacks")


# Create and connect to the database
engine = create_engine(db_path, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session: sqlalchemy.orm.Session = Session()
