"""
Feature 03.a: Order

- The lifecycle of a customer's purchase.
- Cycles through the saved, paid and canclled statuses.
- Stock of a device is decremented on creation and restored on cancellation.
- Cancellation can only be performed while the status is unpaid.
- Contains a total total price derived from its items

NOTE(Tomas): Storing the total price which is a derived value violates 3NF, maybe we should ask the tutor if we can change it.
"""

from ._base import BaseModel
from .user import User
from peewee import IntegerField, DateTimeField, ForeignKeyField, CharField
from datetime import datetime

from enum import StrEnum


class OrderStatus(StrEnum):
    SAVED = "saved"
    PAID = "paid"


class Order(BaseModel):
    user = ForeignKeyField(User, backref="orders", on_delete="CASCADE")
    order_date = DateTimeField(default=datetime.now)
    total_price = IntegerField()  # number of cents
    order_status = CharField(default=OrderStatus.SAVED)
