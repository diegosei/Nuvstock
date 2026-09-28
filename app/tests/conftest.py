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


def test_read_customer_empty(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == []
