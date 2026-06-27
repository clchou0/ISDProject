from flask import Blueprint, Response, make_response, request

from ... import app
from .auth import auth_api
from .device import device_api
from .order import order_api
from .payment import payment_api
from .payment_method import payment_method_api
from .user import user_api

api = Blueprint("api", __name__, url_prefix="/api")


@api.after_request
def return_htmx_if_possible(response: Response):
    # request isn't a htmx request, so just send back the response
    if "HX-Request" not in request.headers:
        return response

    data = response.get_json(silent=True)
    if data is None:
        return response

    if "error" in data:
        return make_response(
            f'<div id="feedback" hx-swap-oob="true"><p class="alert alert-error">{data["error"]}</p></div>'
        )

    if "redirect" in data:
        resp = make_response()
        resp.headers["HX-Redirect"] = data["redirect"]
        return resp

    if "message" in data:
        return make_response(
            f'<div id="feedback" hx-swap-oob="true"><p class="alert alert-success">{data["message"]}</p></div>'
        )

    return response


def register_blueprints():
    api.register_blueprint(auth_api)
    api.register_blueprint(device_api)
    api.register_blueprint(order_api)
    api.register_blueprint(payment_api)
    api.register_blueprint(payment_method_api)
    api.register_blueprint(user_api)
    app.register_blueprint(api)
