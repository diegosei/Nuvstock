def test_read_customer_empty(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_customer(client, customer_payload):
    response = client.post("/customers", json=customer_payload)
    assert response.json()["name"] == customer_payload["name"]
    assert response.status_code == 201


def test_duplicate_email(client, customer_payload):

    first = client.post("/customers", json=customer_payload)
    assert first.status_code == 201

    second = client.post("/customers", json=customer_payload)
    assert second.status_code == 400


def test_invalid_data(client):
    response = client.post(
        "/customers",
        json={
            "name": "Homero",
            "last_name": "Simpson",
            "age": 36,
            "address": "123 fake st.",
            "email": "false_email.gmail.com",
        },
    )
    assert response.status_code == 422


def test_read_customer_for_id(client, customer_payload, create_customer):
    response = create_customer(customer_payload)

    customer_id: int = response["id"]
    response_read = client.get(f"/customers/{customer_id}")
    assert response_read.status_code == 200
    assert response_read.json()["last_name"] == "Simpson"


def test_read_customers(client, customer_payload, create_customer):
    create_customer(customer_payload)
    create_customer(
        {
            **customer_payload,
            "name": "Marge",
            "age": 34,
            "email": "marge_email@gmail.com",
        }
    )
    create_customer(
        {**customer_payload, "name": "Lisa", "age": 8, "email": "lisa_email@gmail.com"}
    )

    response = client.get("/customers")
    assert response.status_code == 200
    assert len(response.json()) == 3

    emails = {customer["email"] for customer in response.json()}
    assert emails == {
        customer_payload["email"],
        "marge_email@gmail.com",
        "lisa_email@gmail.com",
    }


def test_read_customer_not_found(client):
    response = client.get("/customers/9999")
    assert response.status_code == 404


def test_update_customer(client, customer_payload, create_customer):
    customer = create_customer(customer_payload)

    customer_id: int = customer["id"]

    customer_update = client.patch(f"/customers/{customer_id}", json={"age": 39})
    assert customer_update.status_code == 200

    # check resto de campos no cambiaron
    assert customer_update.json()["name"] == customer_payload["name"]
    assert customer_update.json()["email"] == customer_payload["email"]

    response_get = client.get(f"/customers/{customer_id}")
    assert response_get.json()["age"] == 39


def test_update_customer_not_found(client):
    response = client.patch("/customers/9999", json={"age": 30})
    assert response.status_code == 404


def test_update_duplicate_email(client, customer_payload, create_customer):
    create_customer(customer_payload)
    customer_two = create_customer(
        {**customer_payload, "email": "email_check@gmail.com"}
    )
    customer_id: int = customer_two["id"]
    customer_two_update = client.patch(
        f"/customers/{customer_id}", json={"email": customer_payload["email"]}
    )
    assert customer_two_update.status_code == 400

    response_get = client.get(f"/customers/{customer_id}")
    assert response_get.json()["email"] == "email_check@gmail.com"


def test_update_invalid_email(client, customer_payload, create_customer):
    response = create_customer(customer_payload)
    customer_id = response["id"]

    customer_update = client.patch(
        f"/customers/{customer_id}", json={"email": "invalid_mail.gmail.com"}
    )
    assert customer_update.status_code == 422


def test_delete_customer(client, customer_payload, create_customer):
    response = create_customer(customer_payload)

    customer_id: int = response["id"]

    delete_customer = client.delete(f"/customers/{customer_id}")
    assert delete_customer.status_code == 204

    read_deleted = client.get(f"/customers/{customer_id}")
    assert read_deleted.status_code == 404


def test_delete_wrong_id(client):
    response = client.delete("/customers/9999")
    assert response.status_code == 404
