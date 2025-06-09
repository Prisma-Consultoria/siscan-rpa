import os
import sqlite3
import pytest
from main import app, get_db

@pytest.fixture(scope="session")
def test_db(tmp_path_factory, monkeypatch):
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    monkeypatch.setenv("DATABASE_URL", str(db_path))

    conn = sqlite3.connect(str(db_path))
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL
    )""")
    conn.commit()
    conn.close()
    return db_path

@pytest.fixture
def client(test_db):
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client