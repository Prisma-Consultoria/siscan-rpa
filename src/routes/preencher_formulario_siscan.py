from fastapi import APIRouter, Depends

from src.utils.schema import PreencherSolicitacaoInput
from src.utils.dependencies import _get_user_uuid
from src.utils.helpers import run_rpa

router = APIRouter(prefix="/preencher-formulario-siscan", tags=["siscan"])


@router.post(
    "/solicitacao-mamografia",
    summary="Preencher Solicitação de Mamografia",
    description="Executa o RPA para preencher a solicitação de mamografia no SIScan",
)
async def preencher_solicitacao(
    data: PreencherSolicitacaoInput,
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
    uuid: str = Depends(_get_user_uuid),
):
    result = await run_rpa("laudo", data)
    result.update({"user_uuid": uuid})
    return result
