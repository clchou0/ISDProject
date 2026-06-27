"""
Feature 00: Registration and authentication

- Stores user name, email, password, phone, address and status.
- Staff records include a staff ID and position.
"""

from enum import StrEnum

from peewee import CharField, BooleanField

from ._base import BaseModel


class UserRole(StrEnum):
    CUSTOMER = "customer"
    STAFF = "staff"


class User(BaseModel):
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    phone = CharField(null=True)
    role = CharField(default=UserRole.CUSTOMER)
    active = BooleanField(default=True)

    # staff only
    staff_id = CharField(null=True, unique=True)
    position = CharField(null=True)

    # customer only
    address = CharField(null=True)
