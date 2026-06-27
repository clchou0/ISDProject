import pytest
from peewee import SqliteDatabase

from iotbay import app
from iotbay.model import ALL_MODELS
from iotbay.routes import register_blueprints

test_db = SqliteDatabase(":memory:")

register_blueprints()


@pytest.fixture(autouse=True)
def setup_db():
    test_db.bind(ALL_MODELS)
    test_db.connect()
    test_db.create_tables(ALL_MODELS)

    yield

    test_db.drop_tables(ALL_MODELS)
    test_db.close()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c    

@pytest.fixture
def staff_client(client):
    data = {"name": "Tomas", "email": "a@b.com", "password": "mypassword1", "staff_id": "S001", "role": "staff"}
    response = client.post("/api/auth/register", json=data)
    
    assert response.status_code == 201
    client.post(
        "/api/auth/login",
        json={"email": "a@b.com", "password": "mypassword1"},
    )
    assert response.status_code == 201
    return client

@pytest.fixture
def customer_client(client):
    client.post("/api/auth/register", json={
        "name": "Tomas",
        "email": "c@b.com",
        "password": "mypassword1"
    })

    response = client.post("/api/auth/login", json={
        "email": "c@b.com",
        "password": "mypassword1"
    })

    assert response.status_code == 200

    return client