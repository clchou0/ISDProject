from flask import Blueprint, session
from pydantic import BaseModel, EmailStr, Field, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from ...auth import authenticated
from ...model.user import User, UserRole
from ...model.access_log import AccessLog, AccessLogType
from ..utils import PasswordStr, StrippedStr, get_request_data

auth_api = Blueprint("auth", __name__, url_prefix="/auth")


class RegisterBody(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: PasswordStr
    role: str = UserRole.CUSTOMER
    phone: StrippedStr = None
    address: StrippedStr = None
    staff_id: StrippedStr = None
    position: StrippedStr = None


class LoginBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


@auth_api.post("/register")
def register():
    try:
        body = RegisterBody.model_validate(get_request_data())
    except (ValidationError, TypeError):
        return {"error": "Please fill in all required fields"}, 400

    if body.role not in (UserRole.CUSTOMER, UserRole.STAFF):
        return {"error": "Role does not exist"}, 400

    if User.get_or_none(User.email == body.email):
        return {"error": "An account with this email already exists"}, 409

    fields = {
        "name": body.name,
        "email": body.email,
        "password": generate_password_hash(body.password),
        "role": body.role,
        "active": True,
        "phone": body.phone,
        "address": body.address,
    }

    if body.role == UserRole.STAFF:
        if not body.staff_id:
            return {"error": "Staff ID is required for staff registration"}, 400
        if User.get_or_none(User.staff_id == body.staff_id):
            return {"error": "Staff ID already in use"}, 409

        fields["staff_id"] = body.staff_id
        fields["position"] = body.position

    user = User.create(**fields)
    session["user_id"] = user.id
    AccessLog.create(type=AccessLogType.LOGIN, user=user.id)
    return {"redirect": "/"}, 201


@auth_api.post("/login")
def login():
    try:
        body = LoginBody.model_validate(get_request_data())
    except (ValidationError, TypeError):
        return {"error": "Please enter a valid email and password"}, 400

    user = User.get_or_none(User.email == body.email)

    if not user or not check_password_hash(user.password, body.password):
        return {"error": "Invalid email or password"}, 401

    if not user.active:
        return {"error": "Account is deactivated"}, 403

    session["user_id"] = user.id
    AccessLog.create(type=AccessLogType.LOGIN, user=user.id)
    return {"redirect": "/"}, 200


@auth_api.post("/logout")
@authenticated
def logout():
    id = session.pop("user_id", None)
    AccessLog.create(type=AccessLogType.LOGOUT, user=id)
    return {"redirect": "/sign-in"}, 200
