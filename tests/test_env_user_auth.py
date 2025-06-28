import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.env import SISCAN_USER, SISCAN_PASSWORD, SISCAN_URL, get_db
from src.models import User
from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.siscan.context import SiscanBrowserContext


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "env_user.db"
    import src.env as env

    env.init_engine(str(db_file))
    from src import models  # noqa: F401

    env.Base.metadata.create_all(bind=env.engine)
    with TestClient(app) as client:
        yield client


def test_create_user_env(client):
    res = client.post(
        "/cadastrar-usuario",
        json={"username": SISCAN_USER, "password": SISCAN_PASSWORD},
    )
    assert res.status_code == 201
    assert res.json()["message"] == "user created"


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticate_env_user():
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

    print("++++++++++++++++++")
    print(f"User: {SISCAN_USER}, Password: {password}")
    print("++++++++++++++++++")

    req = RequisicaoExameMamografia(
        base_url=SISCAN_URL,
        user=SISCAN_USER,
        password=password,
    )
    req._context = SiscanBrowserContext(
        base_url=SISCAN_URL,
        headless=False,
        timeout=15000,
    )

    print("Iniciando autenticação no SISCAN...")
    await req.authenticate()

    print("Autenticação bem-sucedida!")
    assert await req.context.page.locator(
        'h1:text("SEJA BEM VINDO AO SISCAN")'
    ).is_visible()

    req.context.close()


def test_delete_user_env():
    db = get_db()
    user = db.query(User).filter_by(username=SISCAN_USER).first()
    if user:
        db.delete(user)
        db.commit()
    result = db.query(User).filter_by(username=SISCAN_USER).first()
    db.close()
    assert result is None
