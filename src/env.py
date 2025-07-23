import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from cryptography.hazmat.primitives import serialization

load_dotenv(override=True)

# Determine whether Playwright should run in headless mode. This can be
# controlled via the ``HEADLESS`` environment variable. If the variable is not
# defined, the default is ``True``.
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

PRODUCTION: bool = os.getenv("PRODUCTION", "false").lower() == "true"

TAKE_SCREENSHOT: bool = os.getenv("TAKE_SCREENSHOT", "false").lower() == "true"

DATABASE: str = os.getenv("DATABASE_URL", "database.db")

SISCAN_URL: str = os.getenv("SISCAN_URL", "https://siscan.saude.gov.br/")

SISCAN_USER: str = os.getenv("SISCAN_USER", "")
SISCAN_PASSWORD: str = os.getenv("SISCAN_PASSWORD", "")

DEFAULT_TIMEOUT: int = 10

# Carrega chaves RSA
with open("rsa_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)
with open("rsa_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

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
