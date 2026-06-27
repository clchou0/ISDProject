import pytest
from peewee import IntegrityError
from werkzeug.security import generate_password_hash

from iotbay.model.user import User, UserRole


def _register(client, **overrides):
    """
    Register a sample user
    """
    data = {"name": "Tomas", "email": "a@b.com", "password": "mypassword1"}
    data.update(overrides)
    return client.post("/api/auth/register", json=data)


def _seed_and_login(client):
    User.create(
        name="Tomas",
        email="a@b.com",
        password=generate_password_hash("mypassword1"),
    )
    client.post(
        "/api/auth/login",
        json={"email": "a@b.com", "password": "mypassword1"},
    )


def test_user_model():
    user = User.create(
        name="Tomas",
        email="a@b.com",
        password="pw",
        role=UserRole.STAFF,
        staff_id="S001",
        position="Manager",
    )
    assert user.id is not None
    assert user.role == UserRole.STAFF
    assert user.staff_id == "S001"
    with pytest.raises(IntegrityError):
        User.create(name="Bob", email="a@b.com", password="password")


def test_register(client):
    resp = _register(client)
    assert resp.status_code == 201
    user = User.get(User.email == "a@b.com")
    assert user.name == "Tomas"
    assert user.password != "mypassword1"
    assert client.get("/api/users/me").status_code == 200


def test_register_staff(client):
    resp = _register(client, role="staff", staff_id="S001", email="a@b.com")
    assert resp.status_code == 201
    assert User.get(User.email == "a@b.com").staff_id == "S001"


def test_register_validation(client):
    assert _register(client, email="bad").status_code == 400  # invalid email
    assert _register(client, password="short").status_code == 400  # too short password
    assert (
        _register(client, password="abcdefgh").status_code == 400
    )  # no number in password
    assert (
        _register(client, password="12345678").status_code == 400
    )  # no character in password
    _register(client)
    assert (
        _register(client, name="Bob").status_code == 409
    )  # register with same email (409 conflict)


def test_login(client):
    _seed_and_login(client)
    assert client.get("/api/users/me").status_code == 200


def test_login_rejects(client):
    User.create(
        name="Tomas",
        email="a@b.com",
        password=generate_password_hash("mypassword1"),
        active=False,
    )
    assert (
        client.post(
            "/api/auth/login", json={"email": "a@b.com", "password": "wrong"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "a@b.com", "password": "mypassword1"},
        ).status_code
        == 403
    )


def test_logout(client):
    _seed_and_login(client)
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert client.get("/api/users/me").status_code == 401


def test_get_user(client):
    _seed_and_login(client)
    data = client.get("/api/users/me").get_json()
    assert data["name"] == "Tomas"
    assert "password" not in data


def test_update_user(client):
    _seed_and_login(client)
    resp = client.put(
        "/api/users/me", json={"name": "Tomas", "address": "81 Broadway, Ultimo"}
    )
    assert resp.status_code == 200
    user = User.get(User.email == "a@b.com")
    assert user.name == "Tomas"
    assert user.address == "81 Broadway, Ultimo"


def test_deactivate(client):
    _seed_and_login(client)
    assert client.delete("/api/users/me").status_code == 200
    assert User.get(User.email == "a@b.com").active is False
    assert client.get("/api/users/me").status_code == 401
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "a@b.com", "password": "mypassword1"},
        ).status_code
        == 403
    )
