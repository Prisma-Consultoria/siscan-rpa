import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_laudo_endpoint(client):
    payload = {"campoA": "valorA", "campoB": "valorB"}
    res = client.post("/preencher-laudo-mamografia", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)
