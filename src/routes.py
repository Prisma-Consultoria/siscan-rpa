from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from .env import get_db
from .models import User
from .utils.helpers import _run_rpa
from utils import messages as msg

router = APIRouter()

# Carrega chaves RSA
with open("rsa_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
with open("rsa_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())


@router.post("/cadastrar-usuario", status_code=201)
def cadastrar_usuario(username: str, password: str):

    if not username or not password:
        raise HTTPException(status_code=400, detail=msg.ERR_USERNAME_PASSWORD_REQUIRED)

    encrypted = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    db = get_db()
    try:
        db.add(User(username=username, password=encrypted))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=msg.ERR_USERNAME_EXISTS)
    finally:
        db.close()

    return {"message": msg.USER_CREATED}


@router.post("/preencher-solicitacao-mamografia")
def preencher_solicitacao(data: dict):
    result = _run_rpa("solicitacao", data)
    return result


@router.post("/preencher-laudo-mamografia")
def preencher_laudo(data: dict):
    result = _run_rpa("laudo", data)
    return result
