"""
Feature 04: Payment methods

- Method of payment belonging to a customer only.
- Only viewable by the user it belongs to.
- Stores the payment type
- Deleted when a user account is cancelled

NOTE: Make sure to use ON DELETE CASCADE for simple deletion!
"""

from peewee import CharField, ForeignKeyField

from ._base import BaseModel
from .user import User


class PaymentMethodType:
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    ALL = [CREDIT_CARD, BANK_TRANSFER]


class PaymentMethod(BaseModel):
    user = ForeignKeyField(User, backref="payment_methods", on_delete="CASCADE")

    type = CharField()

    # Store last 4 digits after validation for security
    card_last_four = CharField(null=True)
    card_expiry = CharField(null=True)
    cardholder_name = CharField(null=True)

    account_number = CharField(null=True)
    bsb = CharField(null=True)
    account_name = CharField(null=True)
