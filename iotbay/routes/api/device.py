from flask import Blueprint, render_template, request
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from ...auth import staff, customer
from ...model.device import Device
from ...model.order_item import OrderItem
from ..utils import get_request_data

device_api = Blueprint("device", __name__, url_prefix="/devices")


class CreateDeviceBody(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1)
    price: int = Field(gt=0, description="Price in cents (1995 = $19.95)")
    stock: int = Field(ge=0)


class UpdateDeviceBody(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    type: Optional[str] = Field(min_length=1)
    price: Optional[int] = Field(gt=0, description="Price in cents (1995 = $19.95)")
    stock: Optional[int] = Field(ge=0)


@device_api.get("/")
def get_devices():
    # for: anyone
    # info: list devices, searchable by name and type
    query = request.args.get("query")
    type = request.args.get("type")

    devices = Device.select().where(
        (Device.name.contains(query))
        & (Device.type.contains(type))
        & (Device.is_active)
    )

    return render_template("device/catalogue.html", devices=devices)


@device_api.post("/")
@staff
def create_device():
    # for: staff, admin
    # info: create a new device
    try:
        body = CreateDeviceBody.model_validate(get_request_data())
    except ValidationError as e:
        return {"error": "Invalid device data", "details": e.errors()}, 200

    existing = Device.get_or_none((Device.name == body.name) & Device.is_active)
    if existing:
        return {"error": "A device with this name already exists"}, 200

    device = Device.create(
        name=body.name,
        type=body.type,
        price=body.price,
        stock=body.stock,
        is_active=True,
    )
    print(f"{device.name} created succesfully")
    return render_template("device/row.html", device=device) + render_template(
        "feedback.html", type="success", message=f"{device.name} created succesfully"
    ), 201


@device_api.put("/<int:id>")
@staff
def update_device(id: int):
    # for: staff, admin
    # info: update device details
    device = Device[id]
    # CODE
    try:
        body = UpdateDeviceBody.model_validate(get_request_data())
    except ValidationError:
        return render_template("device/row.html", device=device) + render_template(
            "feedback.html", type="error", message="Invalid device data"
        ), 200

    existing = Device.select().where(
        (Device.name == body.name) & (Device.id != id) & (Device.is_active)
    )
    if existing:
        return render_template("device/row.html", device=device) + render_template(
            "feedback.html",
            type="error",
            message="A device with this name already exists",
        ), 200

    device.name = body.name
    device.type = body.type
    device.price = body.price
    device.stock = body.stock

    device.save()
    return render_template("device/row.html", device=device) + render_template(
        "feedback.html", type="success", message=f"{device.name} updated succesfully"
    ), 200


@device_api.delete("/<int:id>")
@staff
def delete_device(id: int):
    # for: staff, admin
    # info: delete a device
    device = Device.get_or_none(Device.id == id)
    device.is_active = False
    device.save()

    return {"message": "Device deleted Succesfully"}, 200


# Only appears when guided by a link, to edit certain order
@device_api.get("/<int:id>")
@customer
def render_order_edit(id: int):
    items = OrderItem.select().where(OrderItem.order_id == id)
    items_dict = {}

    for item in items:
        items_dict[item.device_id] = item.quantity
    return render_template(
        "device/index.html",
        devices=Device.select().where(Device.is_active),
        order_id=id,
        items=items_dict,
    )
