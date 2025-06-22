import sqlite3
from fastapi import FastAPI, HTTPException
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from playwright.sync_api import sync_playwright
from src.env import PRODUCTION, TAKE_SCREENSHOT, get_db

# Carrega chaves RSA
with open("rsa_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
with open("rsa_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

app = FastAPI()


# Cria tabela de usuários se não existir
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
""")
conn.commit()
conn.close()


@app.post("/cadastrar-usuario", status_code=201)
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


@app.post("/preencher-solicitacao-mamografia")
def preencher_solicitacao(data: dict):
    result = _run_rpa("solicitacao", data)
    return result


@app.post("/preencher-laudo-mamografia")
def preencher_laudo(data: dict):
    result = _run_rpa("laudo", data)
    return result


def _run_rpa(form_type, data):
    screenshots = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not PRODUCTION)
        page = browser.new_page()
        # TODO: implementar login no SISCAN usando CPF/senha de users db

        # TODO: navegar até o formulário e preencher campos com 'data'
        # Exemplo: page.fill("input[name=campo1]", data.get("campo1", ""))

        if not PRODUCTION and TAKE_SCREENSHOT:
            for i in range(1, 4):
                path = f"static/tmp/{form_type}_step{i}.png"
                page.screenshot(path=path)
                screenshots.append(path)

        if PRODUCTION:
            page.click("button[type=submit]")

        browser.close()

    return {"success": True, "screenshots": screenshots}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
