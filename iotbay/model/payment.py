"""
Feature 05: Payments

- Represents a payment for a saved order using a `PaymentMethod`.
- Stores amount, date, and should cause the order status to cycle to "paid".
- Immutable
"""

from ._base import BaseModel


class Payment(BaseModel): ...
