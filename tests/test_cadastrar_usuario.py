import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    import src.env as env

    env.init_engine(str(db_file))
    from src import models  # noqa: F401

    env.Base.metadata.create_all(bind=env.engine)

    with TestClient(app) as client:
        yield client


def test_register_success(client):
    res = client.post(
        "/user", json={"username": "alice", "password": "secret"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["message"] == "user created"


def test_register_missing_fields(client):
    res = client.post("/user", json={"username": "bob"})
    assert res.status_code == 422


def test_register_duplicate(client):
    client.post("/user", json={"username": "eve", "password": "pwd"})
    res = client.post(
        "/user", json={"username": "eve", "password": "pwd2"}
    )
    assert res.status_code == 409
