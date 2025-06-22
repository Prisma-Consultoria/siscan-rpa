import sqlite3
from fastapi import APIRouter, HTTPException
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from env import get_db

router = APIRouter()

# Carrega chaves RSA
with open("rsa_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
with open("rsa_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())


@router.post("/cadastrar-usuario", status_code=201)
def cadastrar_usuario(data: dict):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")

    encrypted = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)", (username, encrypted)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="username already exists")
    finally:
        conn.close()

    return {"message": "user created"}


@router.post("/preencher-solicitacao-mamografia")
def preencher_solicitacao(data: dict):
    from main import _run_rpa
    result = _run_rpa("solicitacao", data)
    return result


@router.post("/preencher-laudo-mamografia")
def preencher_laudo(data: dict):
    from main import _run_rpa
    result = _run_rpa("laudo", data)
    return result
