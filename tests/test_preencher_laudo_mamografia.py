import pytest
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_laudo_endpoint(client):
    payload = {"campoA": "valorA", "campoB": "valorB"}
    res = client.post("/preencher-laudo-mamografia", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)