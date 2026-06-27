from flask import Blueprint, session
from pydantic import BaseModel, EmailStr, Field, ValidationError
from werkzeug.security import generate_password_hash

from playhouse.shortcuts import model_to_dict

from ...auth import authenticated, get_user
from ...model.user import User, UserRole
from ..utils import PasswordStr, StrippedStr, get_request_data

user_api = Blueprint("users", __name__, url_prefix="/users")


class UpdateUserBody(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    password: PasswordStr | None = None
    phone: StrippedStr = None
    address: StrippedStr = None
    position: StrippedStr = None


@user_api.get("/me")
@authenticated
def get_own_user():
    user = get_user()
    assert user is not None

    return model_to_dict(user, exclude=[User.password]), 200


@user_api.put("/me")
@authenticated
def update_own_user():
    data = get_request_data()

    if data.get("password") == "":
        data["password"] = None

    try:
        body = UpdateUserBody.model_validate(data)
    except (ValidationError, TypeError):
        return {"error": "Please fill in all fields correctly"}, 400

    user = get_user()
    assert user is not None

    updates = body.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"]:
        existing = User.get_or_none(User.email == updates["email"])
        if existing and existing.id != user.id:
            return {"error": "Email already in use"}, 409
        user.email = updates["email"]
    if "name" in updates:
        user.name = updates["name"]
    if updates.get("password") is not None:
        user.password = generate_password_hash(updates["password"])
    if "phone" in updates:
        user.phone = updates["phone"]
    if "address" in updates:
        user.address = updates["address"]
    if "position" in updates and user.role == UserRole.STAFF:
        user.position = updates["position"]

    user.save()

    return {"message": "Account updated"}, 200


@user_api.delete("/me")
@authenticated
def delete_own_user():
    user = get_user()
    assert user is not None
    user.active = False
    user.save()
    session.pop("user_id", None)

    return {"redirect": "/sign-in"}, 200


@user_api.get("/me/access-logs")
@authenticated
def get_own_access_logs():
    return ""
