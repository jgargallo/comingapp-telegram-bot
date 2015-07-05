#coding: utf8

import json
from datetime import datetime

from sqlalchemy import (Column, String, Integer, SmallInteger, DateTime,
                        Numeric, ForeignKey)
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref

from settings import MYSQL_ENGINE

Base = declarative_base(MYSQL_ENGINE)

class Chat(Base):
    __tablename__ = 'chat'

    id = Column('id', Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime)
    events = relationship("Event", backref="chat")

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime)

    chat_id = Column(Integer, ForeignKey('chat.id'))
    attendants = relationship("EventAttendant", backref="event")

class Attendant(Base):
    __tablename__ = 'attendant'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created= Column(DateTime)

    events = relationship("EventAttendant", backref="attendant")

class EventAttendant(Base):
    __tablename__ = 'event_attendant'

    id = Column(Integer, primary_key=True)
    # 0/NO, 1/YES, 2/MAYBE
    status = Column(Integer)
    last_updated = Column(DateTime)

    event_id = Column(Integer, ForeignKey('event.id'))
    attendant_id = Column(Integer, ForeignKey('attendant.id'))
