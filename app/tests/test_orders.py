import pytest


def test_read_order_empty(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_create_order(client, order_payload):
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    order_id = response.json()["id"]

    read_order = client.get("/orders")
    assert read_order.status_code == 200

    ids = {order["id"] for order in read_order.json()}
    assert order_id in ids


def test_initial_status(client, order_payload):
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_price_unit(client, order_payload, product_payload):
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    assert response.json()["items"][0]["price_unit"] == product_payload["price"]


def test_order_stock_discount(client, order_payload, product_payload):
    product_id = order_payload["items"][0]["product_id"]
    quantity = order_payload["items"][0]["quantity"]

    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201

    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock"] == product_payload["stock"] - quantity


def test_create_order_customer_non_existent(client, order_payload):
    payload = {**order_payload, "customer_id": 9999}
    response = client.post("/orders", json=payload)
    assert response.status_code == 404

    orders = client.get("/orders")
    assert orders.json() == []


def test_create_order_product_non_existent(client, order_payload):
    payload = {**order_payload, "items": [{"product_id": 9999, "quantity": 1}]}
    response = client.post("/orders", json=payload)
    assert response.status_code == 404

    read_order = client.get("/orders")
    assert read_order.json() == []


def test_create_order_insufficient_stock(client, order_payload, product_payload):
    product_id = order_payload["items"][0]["product_id"]
    payload = {
        **order_payload,
        "items": [{"product_id": product_id, "quantity": product_payload["stock"] + 1}],
    }

    response = client.post("/orders", json=payload)
    assert response.status_code == 400

    read_orders = client.get("/orders")
    assert read_orders.json() == []

    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock"] == product_payload["stock"]


def test_create_order_multiple_items(
    client,
    create_product,
    product_payload,
    create_customer,
    customer_payload,
):
    customer = create_customer(customer_payload)
    product_one = create_product(product_payload)
    product_two = create_product({**product_payload, "name": "mouse", "stock": 10})

    payload = {
        "customer_id": customer["id"],
        "items": [
            {"product_id": product_one["id"], "quantity": 2},
            {"product_id": product_two["id"], "quantity": 3},
        ],
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    assert len(response.json()["items"]) == 2

    stock_one = client.get(f"/products/{product_one['id']}").json()["stock"]
    stock_two = client.get(f"/products/{product_two['id']}").json()["stock"]

    assert stock_one == product_payload["stock"] - 2
    assert stock_two == 10 - 3


def test_create_order_atomicity_multiple_items(
    client, create_customer, customer_payload, create_product, product_payload
):
    customer = create_customer(customer_payload)
    product_one = create_product(product_payload)
    product_two = create_product({**product_payload, "name": "mouse", "stock": 5})

    payload = {
        "customer_id": customer["id"],
        "items": [
            {"product_id": product_one["id"], "quantity": 1},
            {"product_id": product_two["id"], "quantity": 20},
        ],
    }

    response = client.post("/orders", json=payload)
    assert response.status_code == 400

    stock_ok = client.get(f"/products/{product_one['id']}").json()["stock"]
    assert stock_ok == product_payload["stock"]

    read_orders = client.get("/orders")
    assert read_orders.json() == []


def test_create_order_duplicate_product_exceeds_stock(
    client, order_payload, product_payload
):
    product_id = order_payload["items"][0]["product_id"]
    payload = {
        **order_payload,
        "items": [
            {"product_id": product_id, "quantity": 3},
            {"product_id": product_id, "quantity": 3},
        ],
    }

    response = client.post("/orders", json=payload)
    assert response.status_code == 400

    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock"] == product_payload["stock"]


def test_read_order_id(client, order_payload, create_order):
    order = create_order(order_payload)
    order_id = order["id"]

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200


def test_read_order_non_existent_id(client, order_payload):
    response = client.get("/orders/9999")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "setups_steps, new_status, expected_code",
    [
        ([], "paid", 200),  # pending → paid (directo)
        ([], "cancelled", 200),  # pending → cancelled (directo)
        ([], "shipped", 400),  # pending → shipped (inválido, hay que pasar por paid)
        (["paid"], "shipped", 200),  # pending → paid → shipped (válido)
        (
            ["paid", "shipped"],
            "pending",
            400,
        ),  # shipped → pending (inválido, es estado final)
        (["cancelled"], "paid", 400),  # cancelled → paid (inválido, es estado final)
    ],
)
def test_order_status_transition(
    client, order_payload, setups_steps, new_status, expected_code
):
    order = client.post("/orders", json=order_payload).json()
    order_id = order["id"]

    for step in setups_steps:
        prep = client.patch(f"/orders/{order_id}", json={"status": step})
        assert prep.status_code == 200

    response = client.patch(f"/orders/{order_id}", json={"status": new_status})
    assert response.status_code == expected_code


def test_update_status_order_not_found(client):
    response = client.patch("/orders/9999", json={"status": "paid"})
    assert response.status_code == 404


def test_cancel_order_restores_stock(client, order_payload, product_payload):
    product_id = order_payload["items"][0]["product_id"]

    order = client.post("/orders", json=order_payload).json()

    client.patch(f"/orders/{order['id']}", json={"status": "cancelled"})

    product_after = client.get(f"/products/{product_id}")
    assert product_after.json()["stock"] == product_payload["stock"]
