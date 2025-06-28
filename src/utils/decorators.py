from functools import wraps

from fastapi import Header, HTTPException

from .helpers import decode_access_token


def jwt_required(func):
    """FastAPI route decorator to require a valid JWT token."""

    @wraps(func)
    async def wrapper(*args, authorization: str = Header(None), **kwargs):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing token")
        token = authorization.split(" ", 1)[1]
        try:
            decode_access_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="invalid token")
        return await func(*args, **kwargs)

    return wrapper
