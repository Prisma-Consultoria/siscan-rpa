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


def test_solicitacao_endpoint_requires_auth(client, fake_json_file):
    payload = _load_data(Path(fake_json_file))
    res = client.post(
        "/preencher-formulario-siscan/requisicao-mamografia-rastreamento", json=payload
    )
    assert res.status_code == 401


def test_solicitacao_endpoint(client, fake_json_file):
    payload = _load_data(Path(fake_json_file))
    token = create_access_token({"sub": "tester"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/preencher-formulario-siscan/requisicao-mamografia-rastreamento",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["screenshots"], list)


def test_solicitacao_endpoint_validation_errors(client, fake_json_file):
    """Envia payload incompleto e verifica múltiplos erros retornados."""
    payload = _load_data(Path(fake_json_file))
    # remove dois campos obrigatórios para gerar mais de um erro
    payload.pop("cartao_sus", None)
    payload.pop("nome", None)
    token = create_access_token({"sub": "tester"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/preencher-formulario-siscan/requisicao-mamografia-rastreamento",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert isinstance(detail, list) and len(detail) >= 2
