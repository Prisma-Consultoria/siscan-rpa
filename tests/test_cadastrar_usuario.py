import os
import sqlite3
import pytest
from main import app, get_db

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", str(db_file))
    # re-cria a tabela em test.db
    conn = sqlite3.connect(str(db_file))
    conn.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL
    )""")
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

def test_register_success(client):
    res = client.post("/cadastrar-usuario", json={"username": "alice", "password": "secret"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["message"] == "user created"

def test_register_missing_fields(client):
    res = client.post("/cadastrar-usuario", json={"username": "bob"})
    assert res.status_code == 400

def test_register_duplicate(client):
    client.post("/cadastrar-usuario", json={"username": "eve", "password": "pwd"})
    res = client.post("/cadastrar-usuario", json={"username": "eve", "password": "pwd2"})
    assert res.status_code == 409