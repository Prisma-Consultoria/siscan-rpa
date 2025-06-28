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


def test_generate_token(client):
    client.post("/user", json={"username": "alice", "password": "secret"})
    res = client.post(
        "/security/token",
        data={"username": "alice", "password": "secret"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str) and data["access_token"]


def test_invalid_credentials(client):
    res = client.post(
        "/security/token",
        data={"username": "bob", "password": "wrong"},
    )
    assert res.status_code == 401
