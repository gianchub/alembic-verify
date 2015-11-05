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


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True, index=True)
    age = Column(Integer, nullable=False, default=21)
    ssn = Column(Unicode(30), nullable=False)
    number_of_pets = Column(Integer, default=1, nullable=False)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", name="fk_employees_companies"),
        nullable=False
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.id", name="fk_employees_roles"),
        nullable=False
    )


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), nullable=False, unique=True)


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True)
    number = Column(String(40), nullable=False)

    owner = Column(
        Integer,
        ForeignKey("employees.id", name="fk_phone_numbers_employees"),
        nullable=False
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
