from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field
from src.siscan.schema.requisicao_mamografia_schema import RequisicaoMamografiaSchema


class TipoMamografiaRastreamento(Enum):
    POPULACAO_ALVO = "01"
    RISCO_ELEVADO_FAMILIAR = "02"
    CANCER_PREVIO = "03"


class RequisicaoMamografiaRastreamentoSchema(RequisicaoMamografiaSchema):
    tipo_mamografia_de_rastreamento: Annotated[
        Optional[TipoMamografiaRastreamento],
        Field(
            description="Indicação da mamografia de rastreamento: 01=População alvo, 02=Risco elevado, 03=Paciente já tratado",
            json_schema_extra={"x-widget": "radio"},
            title="MAMOGRAFIA DE RASTREAMENTO",
        ),
    ] = None
