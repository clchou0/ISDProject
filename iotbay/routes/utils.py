import re
from typing import Annotated

from flask import request
from pydantic import AfterValidator, BeforeValidator, Field


StrippedStr = Annotated[
    str | None,
    BeforeValidator(lambda v: (v.strip() or None) if isinstance(v, str) else v),
]


def _validate_password(password: str):
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number")

    return password


PasswordStr = Annotated[str, Field(min_length=8), AfterValidator(_validate_password)]


def get_request_data() -> dict[str, str]:
    return request.get_json() if request.is_json else request.form.to_dict()
