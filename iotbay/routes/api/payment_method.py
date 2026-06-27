import re
from datetime import date
from typing import Optional

from flask import Blueprint, request
from pydantic import BaseModel, Field, ValidationError

from ...auth import customer, get_user
from ...model.payment_method import PaymentMethod, PaymentMethodType
from ..utils import get_request_data

payment_method_api = Blueprint(
    "payment_method", __name__, url_prefix="/payment-methods"
)


class CreateCreditCardBody(BaseModel):
    cardholder_name: str = Field(min_length=1, max_length=100)
    card_number: str = Field(min_length=13, max_length=19)
    card_expiry: str = Field(min_length=5, max_length=5)  # MM/YY


class CreateBankTransferBody(BaseModel):
    account_name: str = Field(min_length=1, max_length=100)
    account_number: str = Field(min_length=6, max_length=10)
    bsb: str = Field(min_length=6, max_length=7)  # 6 digits or XXX-XXX


class UpdateCreditCardBody(BaseModel):
    cardholder_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    card_expiry: Optional[str] = Field(default=None, min_length=5, max_length=5)


class UpdateBankTransferBody(BaseModel):
    account_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    account_number: Optional[str] = Field(default=None, min_length=6, max_length=10)
    bsb: Optional[str] = Field(default=None, min_length=6, max_length=7)


def _luhn_check(number: str) -> bool:
    # Validate a card number using Luhn algorithm (US-09.AC2).
    digits = [int(d) for d in number]
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _valid_expiry(expiry: str) -> bool:
    # Check MM/YY format and that the card has not expired.
    if not re.fullmatch(r"\d{2}/\d{2}", expiry):
        return False
    month, year = int(expiry[:2]), 2000 + int(expiry[3:])
    if month < 1 or month > 12:
        return False
    today = date.today()
    return (year, month) >= (today.year, today.month)


def _format_bsb(bsb: str) -> str:
    """Normalise BSB to XXX-XXX."""
    digits = re.sub(r"\D", "", bsb)
    return f"{digits[:3]}-{digits[3:]}"


@payment_method_api.get("/")
@customer
def get_payment_methods():
    # US-09.AC4
    # for: customer
    # info: return own payment methods, searchable by type
    user = get_user()
    assert user is not None

    query = PaymentMethod.select().where(PaymentMethod.user == user)

    type_filter = request.args.get("type", "").strip()
    if type_filter in PaymentMethodType.ALL:
        query = query.where(PaymentMethod.type == type_filter)

    methods = [
        {
            "id": m.id,
            "type": m.type,
            "card_last_four": m.card_last_four,
            "card_expiry": m.card_expiry,
            "cardholder_name": m.cardholder_name,
            "account_number": m.account_number,
            "bsb": m.bsb,
            "account_name": m.account_name,
        }
        for m in query
    ]

    if not methods:
        return {"message": "No payment methods found", "payment_methods": []}, 200

    return {"payment_methods": methods}, 200


@payment_method_api.post("/")
@customer
def create_payment_method():
    # for: customer
    # info: create a payment method, validate with simple algorithm
    user = get_user()
    assert user is not None

    data = get_request_data()
    payment_type = (data.get("type") or "").strip()

    if payment_type == PaymentMethodType.CREDIT_CARD:
        try:
            body = CreateCreditCardBody.model_validate(data)
        except ValidationError:
            return {"error": "Please fill in all credit card fields correctly"}, 400

        card_digits = re.sub(r"\s", "", body.card_number)
        if not card_digits.isdigit():
            return {"error": "Card number must contain only digits"}, 400
        if not _luhn_check(card_digits):
            return {"error": "Card number is invalid"}, 400
        if not _valid_expiry(body.card_expiry):
            return {"error": "Expiry must be MM/YY and must not be in the past"}, 400

        method = PaymentMethod.create(
            user=user,
            type=PaymentMethodType.CREDIT_CARD,
            card_last_four=card_digits[-4:],
            card_expiry=body.card_expiry,
            cardholder_name=body.cardholder_name,
        )

    elif payment_type == PaymentMethodType.BANK_TRANSFER:
        try:
            body = CreateBankTransferBody.model_validate(data)
        except ValidationError:
            return {"error": "Please fill in all bank transfer fields correctly"}, 400

        if not body.account_number.isdigit():
            return {"error": "Account number must contain only digits"}, 400
        if not re.fullmatch(r"\d{3}-?\d{3}", body.bsb):
            return {"error": "BSB must be 6 digits (e.g. 062-000)"}, 400

        method = PaymentMethod.create(
            user=user,
            type=PaymentMethodType.BANK_TRANSFER,
            account_number=body.account_number,
            bsb=_format_bsb(body.bsb),
            account_name=body.account_name,
        )

    else:
        return {"error": "Payment type must be 'credit_card' or 'bank_transfer'"}, 400

    return {"message": "Payment method added successfully", "id": method.id}, 201


@payment_method_api.put("/<int:id>")
@customer
def update_payment_method(id: int):
    # for: customer
    # info: update own payment method
    user = get_user()
    assert user is not None

    method = PaymentMethod.get_or_none(
        (PaymentMethod.id == id) & (PaymentMethod.user == user)
    )
    if method is None:
        return {"error": "Payment method not found"}, 404

    data = get_request_data()

    if method.type == PaymentMethodType.CREDIT_CARD:
        try:
            body = UpdateCreditCardBody.model_validate(data)
        except ValidationError:
            return {"error": "Please fill in all fields correctly"}, 400

        if body.card_expiry is not None:
            if not _valid_expiry(body.card_expiry):
                return {
                    "error": "Expiry must be MM/YY and must not be in the past"
                }, 400
            method.card_expiry = body.card_expiry
        if body.cardholder_name is not None:
            method.cardholder_name = body.cardholder_name

    elif method.type == PaymentMethodType.BANK_TRANSFER:
        try:
            body = UpdateBankTransferBody.model_validate(data)
        except ValidationError:
            return {"error": "Please fill in all fields correctly"}, 400

        if body.account_number is not None:
            if not body.account_number.isdigit():
                return {"error": "Account number must contain only digits"}, 400
            method.account_number = body.account_number
        if body.bsb is not None:
            if not re.fullmatch(r"\d{3}-?\d{3}", body.bsb):
                return {"error": "BSB must be 6 digits (e.g. 062-000)"}, 400
            method.bsb = _format_bsb(body.bsb)
        if body.account_name is not None:
            method.account_name = body.account_name

    method.save()
    return {"message": "Payment method updated"}, 200


@payment_method_api.delete("/<int:id>")
@customer
def delete_payment_method(id: int):
    # for: customer
    # info: delete own payment method
    user = get_user()
    assert user is not None

    method = PaymentMethod.get_or_none(
        (PaymentMethod.id == id) & (PaymentMethod.user == user)
    )
    if method is None:
        return {"error": "Payment method not found"}, 404

    method.delete_instance()
    return {"message": "Payment method deleted"}, 200
