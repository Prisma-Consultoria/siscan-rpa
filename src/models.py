from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import Column, String, LargeBinary, DateTime

from .env import Base


def one_year_from_now() -> datetime:
    """Return a datetime one year from now."""
    return datetime.utcnow() + timedelta(days=365)


class User(Base):
    """Basic user model stored with a UUID primary key."""

    __tablename__ = "users"

    uuid = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    """Model for simple API key authentication."""

    __tablename__ = "api_keys"

    key = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=one_year_from_now)
