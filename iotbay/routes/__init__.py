from flask import Blueprint, render_template

from .. import app, g
from ..auth import authenticated, customer, get_user
from ..db import db
from ..model.access_log import AccessLog
from .api import register_blueprints as register_api_blueprints
from .api.order import get_order_items
from ..model.order import Order, OrderStatus
from datetime import date

from ..model import Device

main = Blueprint("main", __name__)


@main.app_context_processor
def inject_user():
    return {"user": get_user()}


@main.before_request
def before_request():
    g.db = db
    g.db.connect(reuse_if_open=True)


@main.teardown_request
def teardown_request(_):
    if hasattr(g, "db") and not g.db.is_closed():
        g.db.close()


@main.get("/")
def home():
    return render_template("home.html")


@main.get("/devices")
def devices_page():
    return render_template(
        "device/index.html", devices=Device.select().where(Device.is_active)
    )


@main.get("/register")
def register_page():
    return render_template("register.html")


@main.get("/sign-in")
def sign_in_page():
    return render_template("sign-in.html")


@main.get("/account")
@authenticated
def account_page():
    user = get_user()
    return render_template(
        "account.html",
        access_logs=[*AccessLog.select().where(AccessLog.user_id == user.id)],
    )


@main.get("/orders")
@authenticated
def orders_page():
    user = get_user()
    assert user is not None
    orders = []

    if user.role == "staff":
        orders = Order.select()
    else:
        orders = Order.select().where(Order.user == user)

    for order in orders:
        order.items = get_order_items(
            order.id, (order.order_status == OrderStatus.SAVED)
        )

    return render_template(
        "order/index.html",
        orders=orders,
        show_actions=False,
        today=date.today().isoformat,
    )


@main.get("/payment-methods")
@customer
def payment_methods_page():
    return render_template("payment_methods.html")


def register_blueprints():
    app.register_blueprint(main)
    register_api_blueprints()
