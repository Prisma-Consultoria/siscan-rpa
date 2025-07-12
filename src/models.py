from sqlalchemy import Column, Integer, String, LargeBinary

from .env import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
