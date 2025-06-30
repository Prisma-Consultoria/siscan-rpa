import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.env import get_db
from src.models import ApiKey
import secrets


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_laudo_endpoint(client):
    db = get_db()
    key_value = secrets.token_hex(8)
    db.add(ApiKey(key=key_value))
    db.commit()
    db.close()

    payload = {"campoA": "valorA", "campoB": "valorB"}
    res = client.post(
        "/preencher-formulario-siscan/laudo-mamografia",
        json=payload,
        headers={"Api-Key": key_value},
        params={"user_uuid": "test"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)
