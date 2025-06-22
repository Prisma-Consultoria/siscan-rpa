import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
TAKE_SCREENSHOT = os.getenv("TAKE_SCREENSHOT", "false").lower() == "true"
DATABASE = os.getenv("DATABASE_URL", "users.db")

SISCAN_URL = os.getenv("SISCAN_URL", "https://siscan.saude.gov.br/")

# Variáveis de ambiente para fins de teste com python -m src.scrapping
SISCAN_USER = os.getenv("SISCAN_USER", "")
SISCAN_PASSWORD = os.getenv("SISCAN_PASSWORD", "")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn