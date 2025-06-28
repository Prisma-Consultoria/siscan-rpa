import pytest
from fastapi.testclient import TestClient
import secrets
from src.main import app
from src.env import get_db
from src.models import ApiKey


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    import src.env as env

    env.init_engine(str(db_file))
    from src import models  # noqa: F401

    env.Base.metadata.create_all(bind=env.engine)
    key_value = secrets.token_hex(8)
    db = get_db()
    db.add(ApiKey(key=key_value))
    db.commit()
    db.close()

    with TestClient(app) as client:
        yield client, key_value


def test_register_success(client):
    client_obj, key = client
    res = client_obj.post(
        "/user",
        json={"username": "alice", "password": "secret"},
        headers={"Api-Key": key},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["message"] == "user created"


def test_register_missing_fields(client):
    client_obj, key = client
    res = client_obj.post(
        "/user",
        json={"username": "bob"},
        headers={"Api-Key": key},
    )
    assert res.status_code == 422


def test_register_duplicate(client):
    client_obj, key = client
    client_obj.post(
        "/user",
        json={"username": "eve", "password": "pwd"},
        headers={"Api-Key": key},
    )
    res = client_obj.post(
        "/user",
        json={"username": "eve", "password": "pwd2"},
        headers={"Api-Key": key},
    )
    assert res.status_code == 409


def test_register_requires_apikey(client):
    client_obj, _ = client
    res = client_obj.post(
        "/user",
        json={"username": "bob", "password": "x"},
    )
    assert res.status_code == 401
