import pytest
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_solicitacao_endpoint(client):
    payload = {"campo1": "valor1", "campo2": "valor2"}
    res = client.post("/preencher-solicitacao-mamografia", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)