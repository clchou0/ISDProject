from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import redirect, request, session

from .model.user import UserRole, User

P = ParamSpec("P")
T = TypeVar("T")


def get_user() -> User | None:
    """
    Get the currently logged-in user from the session.
    """
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.get_or_none(User.id == user_id)


def _is_api_request() -> bool:
    return request.path.startswith("/api/")


def _role_required(*roles: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Reject requests from users without one of the specified roles.
    """

    def decorator(f: Callable[P, T]) -> Callable[P, T]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            user = get_user()
            if user is None:
                if _is_api_request():
                    return {"error": "You must be signed in"}, 401
                return redirect("/sign-in")
            if user.role not in roles:
                return {"error": "Forbidden"}, 403
            return f(*args, **kwargs)

        return wrapper

    return decorator


def authenticated(f: Callable[P, T]) -> Callable[P, T]:
    """
    Reject requests from unauthenticated users.
    """

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if get_user() is None:
            if _is_api_request():
                return {"error": "You must be signed in"}, 401
            return redirect("/sign-in")
        return f(*args, **kwargs)

    return wrapper


staff = _role_required(UserRole.STAFF)
customer = _role_required(UserRole.CUSTOMER)
