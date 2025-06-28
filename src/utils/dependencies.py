from datetime import datetime

from fastapi import Header, HTTPException

from src.env import get_db
from src.models import ApiKey

from .helpers import decode_access_token


async def jwt_required(authorization: str = Header(None)) -> None:
    """Dependency that validates an Authorization Bearer JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    token = authorization.split(" ", 1)[1]
    try:
        decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


async def api_key_required(api_key: str = Header(None, alias="Api-Key")) -> None:
    """Dependency that validates the Api-Key header."""
    if not api_key:
        raise HTTPException(status_code=401, detail="missing api key")
    db = get_db()
    key = db.query(ApiKey).filter_by(key=api_key).first()
    db.close()
    if not key or key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="invalid api key")
