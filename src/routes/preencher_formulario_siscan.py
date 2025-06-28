from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException

from ..env import get_db
from ..models import ApiKey
from ..utils.helpers import run_rpa, decode_access_token
from ..utils.schema import PreencherSolicitacaoInput

router = APIRouter(prefix="/preencher-formulario-siscan", tags=["siscan"])


def _get_user_uuid(
    user_uuid: str | None = None,
    api_key: str | None = Header(None, alias="Api-Key"),
    authorization: str | None = Header(None),
) -> str:
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="invalid token")
        token = authorization.split(" ", 1)[1]
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
