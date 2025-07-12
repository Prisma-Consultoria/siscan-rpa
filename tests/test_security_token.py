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


def test_generate_token(client):
    client_obj, key = client
    client_obj.post(
        "/user",
        json={"username": "alice", "password": "secret"},
        headers={"Api-Key": key},
    )
    res = client_obj.post(
        "/security/token",
        json={"username": "alice", "password": "secret"},  # <-- troque data por json
    )
    assert res.status_code == 200
    data = res.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str) and data["access_token"]


def test_invalid_credentials(client):
    client_obj, _ = client
    res = client_obj.post(
        "/security/token",
        json={"username": "bob", "password": "wrong"},  # <-- troque data por json
    )
    assert res.status_code == 401
