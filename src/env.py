import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
TAKE_SCREENSHOT = os.getenv("TAKE_SCREENSHOT", "false").lower() == "true"

DATABASE = os.getenv("DATABASE_URL", "users.db")

SISCAN_URL = os.getenv("SISCAN_URL", "https://siscan.saude.gov.br/")

# Variáveis de ambiente para fins de teste com python -m src.scrapping
SISCAN_USER = os.getenv("SISCAN_USER", "")
SISCAN_PASSWORD = os.getenv("SISCAN_PASSWORD", "")

Base = declarative_base()
engine = None
SessionLocal = None


def init_engine(db_path: str | None = None):
    """Initialize database engine and session factory."""
    global DATABASE, engine, SessionLocal
    if db_path is not None:
        DATABASE = db_path
    db_url = DATABASE
    if "://" not in db_url:
        db_url = f"sqlite:///{db_url}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine


# initialize with default DATABASE on import
init_engine()


def get_db():
    """Return a new SQLAlchemy session."""
    return SessionLocal()
