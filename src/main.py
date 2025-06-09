import os
import sqlite3
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from playwright.sync_api import sync_playwright

# Carrega variáveis de ambiente
PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
TAKE_SCREENSHOT = os.getenv("TAKE_SCREENSHOT", "false").lower() == "true"
DATABASE = os.getenv("DATABASE_URL", "users.db")

# Carrega chaves RSA
with open("rsa_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
with open("rsa_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route("/cadastrar-usuario", methods=["POST"])
def cadastrar_usuario():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    encrypted = public_key.encrypt(
        password.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (username, encrypted)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "username already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": "user created"}), 201

@app.route("/preencher-solicitacao-mamografia", methods=["POST"])
def preencher_solicitacao():
    data = request.get_json() or {}
    result = _run_rpa("solicitacao", data)
    return jsonify(result), 200

@app.route("/preencher-laudo-mamografia", methods=["POST"])
def preencher_laudo():
    data = request.get_json() or {}
    result = _run_rpa("laudo", data)
    return jsonify(result), 200

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
    app.run(host="0.0.0.0", port=5000)