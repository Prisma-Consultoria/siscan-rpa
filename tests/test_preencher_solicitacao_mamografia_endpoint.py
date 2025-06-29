import pytest
from fastapi.testclient import TestClient
from src.main import app
from pathlib import Path
from src.utils.validator import Validator
from src.utils.helpers import create_access_token


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def _load_data(path):
    return Validator.load_json(path)


def test_solicitacao_endpoint_requires_auth(client, fake_json_rastreio_file):
    payload = _load_data(Path(fake_json_rastreio_file))
    res = client.post(
        "/preencher-formulario-siscan/solicitacao-mamografia", json=payload
    )
    assert res.status_code == 401


def test_solicitacao_endpoint(client, fake_json_rastreio_file):
    payload = _load_data(Path(fake_json_rastreio_file))
    token = create_access_token({"sub": "tester"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/preencher-formulario-siscan/solicitacao-mamografia",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)
