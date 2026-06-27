"""
Feature 02: IoT device catalogue management

- Represents an IoT product with a name, type, unit price, and stock.
- Only staff can create, update or delete devices.
- All users can search devices by name or type.
"""

from ._base import BaseModel
from peewee import CharField, IntegerField, BooleanField


class Device(BaseModel):
    name = CharField()
    type = CharField()
    price = IntegerField()  # IMPORTANT: INTEGER NUMBER OF CENTS
    stock = IntegerField()
    is_active = BooleanField(default=True)
