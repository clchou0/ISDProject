"""
Database models defined with Peewee ORM

For group members:
    - Each file in this directory represents a model of the IoTBay Marketplace.
    - To learn how to define the models, read this documentation: https://github.com/coleifer/peewee
"""

# fmt: off
from .user import User                      # feat 00
from .access_log import AccessLog           # feat 01
from .device import Device                  # feat 02
from .order import Order                    # feat 03.a
from .order_item import OrderItem           # feat 03.b
from .payment_method import PaymentMethod   # feat 04
from .payment import Payment                # feat 05
# fmt: on

ALL_MODELS = [
    User,
    AccessLog,
    Device,
    Order,
    OrderItem,
    PaymentMethod,
    Payment,
]
