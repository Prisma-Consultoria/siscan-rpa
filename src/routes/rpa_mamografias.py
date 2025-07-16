from fastapi import APIRouter, Depends

from src.routes.auth.dependencies import get_current_user_uuid
from src.siscan.rpa.runner import run_rpa
from src.siscan.schema.requisicao_mamografia_diagnostica_schema import \
    RequisicaoMamografiaDiagnosticaSchema
from src.siscan.schema.requisicao_mamografia_rastreamento_schema import \
    RequisicaoMamografiaRastreamentoSchema


router = APIRouter(prefix="/api/v1/mamografias", tags=["mamografias"])


@router.post(
    "/requisicoes-rastreamento",
    summary="Requisição de Mamografia de Rastreamento",
    description="Executa o RPA para preencher a requisição de mamografia de "
                "rastreamento na interface web do SISCAN",
)
async def preencher_requisicao_rastreamento(
    data: RequisicaoMamografiaRastreamentoSchema,
    uuid: str = Depends(get_current_user_uuid),
):
    result = await run_rpa("requisicao-rastreamento", data.__dict__)
    result.update({"user_uuid": uuid})
    return result

@router.post(
    "/requisicoes-diagnostica",
    summary="Requisição de Mamografia de Diagnóstica",
    description="Executa o RPA para preencher a requisição de mamografia de "
                "diagnóstica na interface web do SISCAN",
)
async def preencher_requisicao_diagnostica(
    data: RequisicaoMamografiaDiagnosticaSchema,
    uuid: str = Depends(get_current_user_uuid),
):
    result = await run_rpa("requisicao-diagnostica", data.__dict__)
    result.update({"user_uuid": uuid})
    return result

@router.post(
    "/laudos",
    summary="Preencher Laudo de Mamografia",
    description="Executa o RPA para preencher o laudo de mamografia no SIScan",
)
async def preencher_laudo(
    data: dict,
    uuid: str = Depends(get_current_user_uuid),
):
    result = await run_rpa("laudo", data)
    result.update({"user_uuid": uuid})
    return result
