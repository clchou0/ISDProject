from flask import Blueprint, render_template, request, flash, session
from pydantic import BaseModel, Field
from typing import Optional
from ...model.user import User
from ...model.device import Device
from ...model.order import Order, OrderStatus
from ...model.order_item import OrderItem
from ..utils import get_request_data
from ...auth import customer, get_user, authenticated
from datetime import datetime
from typing import List
from ...db import db

order_api = Blueprint("order", __name__, url_prefix="/orders")


class CreateOrderItemBody(BaseModel):
    device_id: int = Field(gt=0)
    unit_price: int = Field(gt=0)
    quantity: int = Field(gt=0)


class CreateOrderBody(BaseModel):
    total_price: int = Field(gt=0)
    items: List[CreateOrderItemBody]


class UpdateOrderBody(BaseModel):
    order_date: Optional[datetime] = Field(default_factory=datetime.now)
    items: Optional[List[CreateOrderItemBody]] = None


# Returns visualization of items in the order, saved is the only option that is not paid
def get_order_items(order_id, saved):
    valid_items = []
    items = OrderItem.select().where(OrderItem.order_id == order_id)
    # Determines if u can pay for an order

    for item in items:
        device = Device.get_or_none(Device.id == item.device_id)
        item.device_name = device.name

        if not device.is_active:
            if not saved:
                item.device_name += " (discontinued)"
            else:
                item.device_name = "⚠" + item.device_name

        # For the visual
        valid_items.append(item)
    return valid_items


@order_api.get("/")
@authenticated
def get_orders():
    # for: customer, staff, admin
    # info: customer sees own orders, staff/admin sees all orders, searchable by order id and date

    user = get_user()
    assert user is not None
    query = Order.select()

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    saved = request.args.get("saved")
    paid = request.args.get("paid")
    user_args = request.args.get("user")

    if user.role != "staff":
        query = query.where(Order.user == user)

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

        query = query.where(Order.order_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59
        )
        query = query.where(Order.order_date <= end_date)

    status = []
    if saved:
        status.append(OrderStatus.SAVED)
    if paid:
        status.append(OrderStatus.PAID)
    query = query.where(Order.order_status.in_(status))

    if user.role == "staff" and user_args:
        try:
            parsed = int(user_args)
            query = query.join(User).where(User.id == parsed)
        except ValueError:
            query = query.join(User).where(User.name.contains(user_args))

    orders = query.execute()

    for order in orders:
        order.items = get_order_items(
            order.id, (order.order_status == OrderStatus.SAVED)
        )

    return render_template("order/table.html", orders=orders, show_actions=False)


# Update order items on device catalogue (naive cart), snaps back to
@order_api.post("/update/<int:id>/<int:prev>")
@authenticated
def validate_qn(id: int, prev: int):
    data = request.form
    qty = data.get(str(id), 0)
    qty = int(qty)

    device = Device.get_by_id(id)
    # Factor in what order originally was
    validated_qty = max(0, min(device.stock + prev, qty))

    return f'''<input type="number" name="{id}" min="0" max="{device.stock + prev}" 
        value="{validated_qty}" hx-post="/api/orders/update/{id}" 
        hx-trigger="change delay:10ms" hx-target="this" hx-swap="outerHTML">'''


# Helper: adds items to selected order id based on the device-quantity mapping
def add_items(order_id, items):
    total_price = 0
    for device_id, quantity_str in items:
        if quantity_str and int(quantity_str) > 0:
            quantity = int(quantity_str)
            device_id = int(device_id)

            try:
                device = Device.get_by_id(device_id)
            except Device.DoesNotExist:
                raise ValueError(f"Device {device.name} could have been deleted")

            if not device.is_active:
                raise ValueError(f"Device {device.name} could have been deleted")
            if device.stock < quantity:
                raise ValueError(f"Please insert a valid number for {device.name}")

            # Flag to determine whether anything is in the cart
            unit_price = device.price
            total_price += unit_price * quantity
            OrderItem.create(
                order_id=order_id,
                device_id=device_id,
                quantity=quantity,
                unit_price=unit_price,
            )
            # Processing for single device stock
            device.stock -= quantity
            device.save()

    return total_price


@order_api.post("/")
@customer
def create_order():
    user = get_user()
    assert user is not None

    # Get form data
    raw_data = get_request_data()

    # Process form data - now device_id is the key directly
    total_price = 0

    try:
        with db.atomic():
            newOrder = Order.create(
                order_date=datetime.now(),
                user=user,
                total_price=0,
                order_status=OrderStatus.SAVED,
            )

            # device to quantity mapping
            total_price = add_items(newOrder.id, raw_data.items())

            if total_price == 0:
                raise ValueError("Please place items in your cart!")

            newOrder.total_price = total_price
            newOrder.save()

    except ValueError as e:
        return render_template("feedback.html", type="error", message=str(e)), 200
    except Exception as e:
        return str(e), 500

    flash({"type": "success", "message": f"Order #{newOrder.id} has been created"})
    return "", 204, {"HX-Redirect": "/orders"}


# Helper: removes items based on the order id given
def remove_items(id: int):
    items = OrderItem.select().where(OrderItem.order_id == id)
    for item in items:
        device = Device.get_or_none(item.device_id)
        if device is None:
            raise ValueError("Device is not found")
        # Adds back to the stock as the order is revoked
        device.stock += item.quantity
        device.save()
    # Eventually clears out every item
    OrderItem.delete().where(OrderItem.order_id == id).execute()
    return


@order_api.put("/<int:id>")
@customer
def update_order(id: int):
    # for: customer
    # info: update a saved order before it is paid. if status is set to cancelled, restore stock

    user = get_user()
    assert user is not None
    order = Order.get_or_none((Order.id == id) & (Order.user == user))

    if order is None:
        return {"error": "Order not found"}, 404
    if order.order_status == OrderStatus.PAID:
        return {"error": "Payment has already been made for order"}, 400

    raw_data = get_request_data()
    total_price = 0

    try:
        with db.atomic():
            # removing all original order items
            remove_items(id)
            # add new set of items
            total_price = add_items(id, raw_data.items())

            order.total_price = total_price
            order.save()

            if total_price == 0:
                raise ValueError("Please place items in your cart!")

    except ValueError as e:
        return render_template("feedback.html", type="error", message=str(e)), 200
    except Exception as e:
        return str(e), 500

    flash({"type": "success", "message": f"Order #{id} has been updated"})
    return "", 204, {"HX-Redirect": "/orders"}


@order_api.delete("/<int:id>")
@customer
def delete_order(id: int):
    user = get_user()
    assert user is not None

    order = Order.get_or_none((Order.id == id) & (Order.user == user))
    if order is None:
        return {"error": "Order not found"}, 404
    if order.order_status == OrderStatus.PAID:
        return render_template(
            "feedback.html",
            type="error",
            message=f"Payment has already been made for order #{id}",
        ), 200

    try:
        with db.atomic():
            remove_items(id)
            Order.delete().where(Order.id == id).execute()
    except ValueError as e:
        return render_template("feedback.html", type="error", message=str(e)), 200
    except Exception as e:
        return str(e), 500

    return render_template(
        "feedback.html", type="success", message=f"Order #{id} has been deleted"
    )


# Eligible for making a payment will lead u to paying it
@order_api.post("/checkout/<int:id>")
@customer
def proceed_checkout(id: int):
    user = get_user()
    assert user is not None

    order = Order.get_or_none((Order.id == id) & (Order.user == user))
    if order is None:
        return {"error": "Order not found"}, 404
    if order.order_status == OrderStatus.PAID:
        return render_template(
            "feedback.html",
            type="error",
            message=f"Payment has already been made for order #{id}",
        ), 200

    inactive_names = check_order_items(id)
    if inactive_names:
        result = ", ".join(f"[{name.name}]" for name in inactive_names)
        result = "Items " + result + " have been discontinued, please update your order"
        return render_template("feedback.html", type="error", message=result), 200

    return "", 204, {"HX-Redirect": f"/api/orders/{id}/payment"}


# Checks if there is any order item that contains a discontinued product
def check_order_items(id: int):
    inactive_names = (
        Device.select(Device.name)
        .join(OrderItem, on=(OrderItem.device_id == Device.id))
        .where(OrderItem.order_id == id, not Device.is_active)
    )
    return inactive_names


@order_api.get("/<int:id>/payment")
@customer
def payment_page(id: int):
    user = get_user()
    assert user is not None
    order = Order.get_or_none((Order.id == id) & (Order.user == user))

    if order is None:
        return {"error": "Order not found"}, 404
    if order.order_status != OrderStatus.SAVED:
        return {"error": "Payment has already been made for order"}, 400

    items = get_order_items(order.id, order.order_status == OrderStatus.SAVED)

    return render_template(
        "payment.html", id=f"{id}", items=items, total_price=order.total_price
    )


@order_api.post("/toggle-actions")
def toggle_actions():
    return render_template(
        "order/table.html", show_actions=not session.get("show_actions")
    )
    # return '', 204
