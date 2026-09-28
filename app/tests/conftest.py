import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.database import get_session
from app.main import app

sqlite_url = "sqlite://"

engine = create_engine(
    sqlite_url, connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_overrides():
        return session

    app.dependency_overrides[get_session] = get_session_overrides

    client = TestClient(app=app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="customer_payload")
def customer_payload_fixture():
    return {
        "name": "Homero",
        "last_name": "Simpson",
        "age": 36,
        "address": "123 fake st.",
        "email": "false_email@gmail.com",
    }


@pytest.fixture(name="create_customer")
def create_customer_fixture(client):
    def _create(payload: dict):
        response = client.post("/customers", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create


@pytest.fixture(name="product_payload")
def product_payload_fixture():
    return {"name": "keyboard", "price": 45000, "stock": 5}


@pytest.fixture(name="create_product")
def create_product_fixture(client):
    def _create(payload: dict):
        response = client.post("/products", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create
