from flask import Blueprint, render_template
from ...model.order import Order, OrderStatus
from ...auth import customer, get_user, authenticated
from .order import check_order_items


payment_api = Blueprint("payment", __name__, url_prefix="/payments")


@payment_api.get("/")
@authenticated
def get_payments():
    # for: customer, staff, admin
    # info: customer sees own payments, staff/admin sees all
    return ""


# Dummy implementation: does not create a payment receipt
# Would change order status to paid
@payment_api.post("/<int:id>")
@customer
def create_payment(id: int):
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

    # Check order if anything within it is discontinued
    inactive_names = check_order_items(id)
    if inactive_names:
        result = ", ".join(f"[{name.name}]" for name in inactive_names)
        result = "Items " + result + " have been discontinued, please update your order"
        return render_template("feedback.html", type="error", message=result), 200

    order.order_status = OrderStatus.PAID
    order.save()

    return "", 204, {"HX-Redirect": "/orders"}


@payment_api.get("/<int:id>")
@customer
def view_payment(id: int):
    return render_template("make_payment.html", id=f"{id}")
