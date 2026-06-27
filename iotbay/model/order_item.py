"""
Feature 03.b: Order item

- An item within an order.
- Stores the device, quantity, and unit price at the time of the order.
- Functions as an associative entity for `Device` and `Order`
"""

from ._base import BaseModel
from peewee import IntegerField


class OrderItem(BaseModel):
    unit_price = IntegerField()
    device_id = IntegerField()
    quantity = IntegerField()
    order_id = IntegerField()
