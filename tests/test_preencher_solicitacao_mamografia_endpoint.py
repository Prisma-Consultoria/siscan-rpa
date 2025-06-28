import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_solicitacao_endpoint(client):
    payload = {"campo1": "valor1", "campo2": "valor2"}
    res = client.post("/preencher-solicitacao-mamografia", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)
