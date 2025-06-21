import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
TAKE_SCREENSHOT = os.getenv("TAKE_SCREENSHOT", "false").lower() == "true"
DATABASE = os.getenv("DATABASE_URL", "users.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn