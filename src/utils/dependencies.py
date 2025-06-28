from fastapi import Header, HTTPException

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

