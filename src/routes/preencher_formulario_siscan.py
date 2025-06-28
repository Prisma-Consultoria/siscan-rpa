from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from ..env import get_db
from ..models import ApiKey
from ..utils.helpers import run_rpa, decode_access_token
from ..utils.schema import PreencherSolicitacaoInput

# Security schemes
api_key_scheme = APIKeyHeader(name="Api-Key", auto_error=False)
oauth2_optional = OAuth2PasswordBearer(tokenUrl="security/token", auto_error=False)

router = APIRouter(prefix="/preencher-formulario-siscan", tags=["siscan"])


def _get_user_uuid(
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


@router.post(
    "/solicitacao-mamografia",
    summary="Preencher Solicitação de Mamografia",
    description="Executa o RPA para preencher a solicitação de mamografia no SIScan",
)
async def preencher_solicitacao(
    data: PreencherSolicitacaoInput,
    user_uuid: str | None = None,
    uuid: str = Depends(_get_user_uuid),
):
    result = await run_rpa("solicitacao", data.__dict__)
    result.update({"user_uuid": uuid})
    return result


@router.post(
    "/laudo-mamografia",
    summary="Preencher Laudo de Mamografia",
    description="Executa o RPA para preencher o laudo de mamografia no SIScan",
)
async def preencher_laudo(
    data: dict,
    user_uuid: str | None = None,
    uuid: str = Depends(_get_user_uuid),
):
    result = await run_rpa("laudo", data)
    result.update({"user_uuid": uuid})
    return result
