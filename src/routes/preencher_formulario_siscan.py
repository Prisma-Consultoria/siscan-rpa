from fastapi import APIRouter, Depends

from src.utils.schema import PreencherSolicitacaoInput
from src.utils.dependencies import _get_user_uuid
from src.utils.helpers import run_rpa

router = APIRouter(prefix="/preencher-formulario-siscan", tags=["siscan"])


@router.post(
    "/requisicao-mamografia-rastreamento",
    summary="Requisição de Mamografia de Rastreamento",
    description="Executa o RPA para preencher a requisição de mamografia de rastreamento na interface web do SISCAN",
)
async def preencher_requisicao_mamografia_rastreamento(
    data: PreencherSolicitacaoInput,
    uuid: str = Depends(_get_user_uuid),
):
    result = await run_rpa("requisicao-rastreamento", data.__dict__)
    result.update({"user_uuid": uuid})
    return result

@router.post(
    "/requisicao-mamografia-diagnostica",
    summary="Requisição de Mamografia de Diagnóstica",
    description="Executa o RPA para preencher a requisição de mamografia de diagnóstica na interface web do SISCAN",
)
async def preencher_requisicao_mamografia_diagnostica(
    data: PreencherSolicitacaoInput,
    uuid: str = Depends(_get_user_uuid),
):
    result = await run_rpa("requisicao-diagnostica", data.__dict__)
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
