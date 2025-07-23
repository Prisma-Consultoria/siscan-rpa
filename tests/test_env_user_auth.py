import pytest
from fastapi.testclient import TestClient
import secrets

from src.main import app
from src.env import SISCAN_USER, SISCAN_PASSWORD, SISCAN_URL, get_db
from src.models import User, ApiKey
from src.siscan.classes.requisicao_exame_mamografia_rastreio import (
    RequisicaoExameMamografiaRastreio,
)
from src.siscan.context import SiscanBrowserContext


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "test.db"
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


def test_create_user_env(client):
    client_obj, key = client
    res = client_obj.post(
        "/user",
        json={"username": SISCAN_USER, "password": SISCAN_PASSWORD},
        headers={"Api-Key": key},
    )
    assert res.status_code == 201
    assert res.json()["message"] == "user created"


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticate_env_user(headless: bool):
    # Captura o usuário e senha do banco de dados, tomando o usuário como chave única
    db = get_db()
    user = db.query(User).filter_by(username=SISCAN_USER).first()
    db.close()
    assert user is not None, "User not found in the database"

    # Descriptografa a senha usando a mesma tecnologia de criptografia (RSA)
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from src.env import private_key  # Certifique-se de importar a chave privada correta

    password = private_key.decrypt(
        user.password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    ).decode()

    req = RequisicaoExameMamografiaRastreio(
        base_url=SISCAN_URL,
        user=SISCAN_USER,
        password=password,
    )
    req._context = SiscanBrowserContext(
        base_url=SISCAN_URL,
        headless=headless,
        timeout=15000,
    )

    await req._authenticate()

    assert await (
        (await req.context.page).locator('h1:text("SEJA BEM VINDO AO SISCAN")')
    ).is_visible()

    await req.context.close()


def test_delete_user_env():
    db = get_db()
    user = db.query(User).filter_by(username=SISCAN_USER).first()
    if user:
        db.delete(user)
        db.commit()
    result = db.query(User).filter_by(username=SISCAN_USER).first()
    db.close()
    assert result is None
