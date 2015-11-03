# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Enum, ForeignKey, Integer, String, Unicode
)
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)
    mysql_character_set = "utf8"

    def delete(self):
        if self.deleted_at is None:
            self.deleted_at = datetime.utcnow()


Base = declarative_base(cls=Base)


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True, index=True)
    age = Column(Integer, nullable=True)
    favourite_pet = Column(Enum(u"cat", u"dog", u"other"), nullable=True)


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True)
    number = Column(String(40), nullable=True)
    person_id = Column(
        Integer,
        ForeignKey("people.id"),
        nullable=False
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    address = Column(Unicode(200), nullable=True)
    zip_code = Column(Unicode(20), nullable=True)
    city = Column(Unicode(100), nullable=True)
    country = Column(Unicode(3), nullable=True)

    person_id = Column(
        Integer,
        ForeignKey("people.id"),
        nullable=False
    )
