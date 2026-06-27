import pytest

from iotbay import app
from iotbay.model.device import Device
from iotbay.model import ALL_MODELS

def seed_device(name, type, price=1995, stock=10):
    return Device.create(
        name=name,
        type=type,
        price=price,
        stock=stock
    )

def seed_devices():
    return [
        seed_device("MacBook Pro", "laptop", price=2500, stock=15),
        seed_device("iPhone 15", "phone", price=1000, stock=50),
        seed_device("iPad Air", "tablet", price=750, stock=30),
        seed_device("AirPods Pro", "audio", price=250, stock=100),
        seed_device("Apple Watch", "wearable", price=400, stock=25),
    ]

def place_order(client, items: dict[int, int]):
    payload = [
        {"device_id": device_id, "quantity": qty}
        for device_id, qty in items.items()
    ]

    return client.post("/api/orders/", json={"items": payload})

@pytest.fixture
def seed_all(customer_client, staff_client):
    return {
        "devices": seed_devices(),
        "customer_client": customer_client,
        "staff_client": staff_client,
    }

def test_place_order(seed_all, authed_client):
    devices = seed_all["devices"]
    client = authed_client

    response = client.post("/api/orders/", json={
        "items": [
            {"device_id": devices[0].id, "quantity": 2}
        ]
    })

    print(response.data.decode())
    assert response.status_code == 201