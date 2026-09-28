def test_read_product_empty(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client, product_payload):
    product = client.post("/products", json=product_payload)

    assert product.status_code == 201

    product_id: int = product.json()["id"]
    read_product = client.get(f"/products/{product_id}")

    assert read_product.status_code == 200
    assert read_product.json()["name"] == product_payload["name"]


def test_create_product_invalid_data(client):
    product = client.post(
        "/products", json={"name": "keyboard", "price": "asd", "stock": 50}
    )
    assert product.status_code == 422


def test_create_product_zero_price(client):
    product = client.post(
        "/products", json={"name": "keyboard", "price": 0, "stock": 50}
    )
    assert product.status_code == 201


def test_create_product_zero_stock(client):
    product = client.post(
        "/products", json={"name": "keyboard", "price": 20000, "stock": 0}
    )
    assert product.status_code == 201


def test_create_product_negative_price(client):
    product = client.post(
        "/products", json={"name": "keyboard", "price": -200, "stock": 50}
    )
    assert product.status_code == 422


def test_create_product_negative_stock(client):
    product = client.post(
        "/products", json={"name": "keyboard", "price": 20000, "stock": -10}
    )
    assert product.status_code == 422


def test_read_product_for_id(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id = product["id"]
    response_read = client.get(f"/products/{product_id}")
    assert response_read.status_code == 200
    assert response_read.json()["id"] == product_id
    assert response_read.json()["price"] == product_payload["price"]


def test_read_products(client, product_payload, create_product):
    create_product(product_payload)
    create_product({**product_payload, "name": "mouse", "price": 38000})
    read_products = client.get("/products")

    assert read_products.status_code == 200

    names = {product["name"] for product in read_products.json()}
    assert len(read_products.json()) == 2
    assert names == {product_payload["name"], "mouse"}


def test_read_product_not_found(client):
    response = client.get("/products/9999")
    assert response.status_code == 404


def test_update_product_price(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id: int = product["id"]
    update_product = client.patch(f"/products/{product_id}", json={"price": 38000})
    assert update_product.status_code == 200

    read_update = client.get(f"/products/{product_id}")
    assert read_update.json()["price"] == 38000
    assert read_update.json()["name"] == product_payload["name"]


def test_update_product_stock(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id: int = product["id"]
    update_product = client.patch(f"/products/{product_id}", json={"stock": 50})
    assert update_product.status_code == 200

    read_update = client.get(f"/products/{product_id}")
    assert read_update.json()["stock"] == 50
    assert read_update.json()["name"] == product_payload["name"]


def test_update_product_not_found(client):
    response = client.patch("/products/9999", json={"name": "cpu"})
    assert response.status_code == 404


def test_update_product_negative_price(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id = product["id"]
    update_product = client.patch(f"/products/{product_id}", json={"price": -200})
    assert update_product.status_code == 422

    read_product = client.get(f"/products/{product_id}")
    assert read_product.status_code == 200
    assert read_product.json()["price"] == product_payload["price"]


def test_update_product_negative_stock(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id = product["id"]
    update_product = client.patch(f"/products/{product_id}", json={"stock": -200})
    assert update_product.status_code == 422

    read_product = client.get(f"/products/{product_id}")
    assert read_product.status_code == 200
    assert read_product.json()["stock"] == product_payload["stock"]


def test_delete_product(client, product_payload, create_product):
    product = create_product(product_payload)
    product_id: int = product["id"]

    delete_product = client.delete(f"/products/{product_id}")
    assert delete_product.status_code == 204

    read_product = client.get(f"/products/{product_id}")
    assert read_product.status_code == 404


def test_delete_wrong_product(client):
    response = client.delete("/products/9999")
    assert response.status_code == 404
