from datetime import datetime
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from src.env import get_db
from src.models import ApiKey
from src.routes.auth.utils import decode_access_token

api_key_scheme = APIKeyHeader(name="Api-Key", auto_error=False)
oauth2_optional = OAuth2PasswordBearer(tokenUrl="security/token", auto_error=False)

api_key_required = APIKeyHeader(
    name="Api-Key",
    auto_error=True,
)


def get_current_user_uuid(
    user_uuid: str | None = None,
    token: str | None = Security(oauth2_optional),
    api_key: str | None = Security(api_key_scheme),
) -> str:
    """Return the user UUID from a valid JWT or API key."""
    if token:
        payload = decode_access_token(token)
        return payload.get("sub")
    if api_key:
        db = get_db()
        key = db.query(ApiKey).filter_by(key=api_key).first()
        db.close()
        if not key or key.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="invalid api key")
        if not user_uuid:
            raise HTTPException(status_code=400, detail="user_uuid required")
        return user_uuid
    raise HTTPException(status_code=401, detail="missing credentials")
