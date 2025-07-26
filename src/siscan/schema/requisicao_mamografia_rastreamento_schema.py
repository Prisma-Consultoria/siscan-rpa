from __future__ import annotations

import logging

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field
from pydantic.functional_validators import model_validator

from src.siscan.schema import TipoDeMamografia
from src.siscan.schema.requisicao_mamografia_schema import RequisicaoMamografiaSchema

logger = logging.getLogger(__name__)


class TipoMamografiaRastreamento(Enum):
    POPULACAO_ALVO = "01"
    RISCO_ELEVADO_FAMILIAR = "02"
    CANCER_PREVIO = "03"


class RequisicaoMamografiaRastreamentoSchema(RequisicaoMamografiaSchema):
    # Mamografia de Rastreamento
    # Mamografia realizada nas mulheres assintomáticas (sem sinais e sintomas
    # de câncer de mama), com idade entre 50 e 69 anos (população alvo) ou
    # maiores de 35 anos com histórico familiar (
    # População de risco elevado - história familiar)
    # ou histórico pessoal de câncer de mama (pacientes já tratados)
    # Atenção: mastalgia não é sinal de câncer de mama

    tipo_mamografia_de_rastreamento: Annotated[
        Optional[TipoMamografiaRastreamento],
        Field(
            description="Indicação da mamografia de rastreamento: "
                        "01=População alvo, 02=Risco elevado, "
                        "03=Paciente já tratado",
            json_schema_extra={"x-widget": "radio", "x-xpath": ""},
            title="MAMOGRAFIA DE RASTREAMENTO",
        ),
    ] = None

    @model_validator(mode="after")
    def valida_tipo_de_mamografia(cls, values):
        logger.debug(
            f"Executando valida_tipo_de_mamografia, valores: {values}")

        # 5) Se tipo_de_mamografia == 'Rastreamento', tipo_mamografia_de_rastreamento é obrigatório
        tipo = values.tipo_de_mamografia
        mamo = values.tipo_mamografia_de_rastreamento
        if tipo == TipoDeMamografia.RASTREAMENTO and not mamo:
            raise ValueError(
                "Se tipo_de_mamografia = Rastreamento, precisa informar 'tipo_mamografia_de_rastreamento'."
            )
        if tipo != TipoDeMamografia.RASTREAMENTO and mamo:
            raise ValueError(
                "Se tipo_de_mamografia ≠ Rastreamento, não deve informar 'tipo_mamografia_de_rastreamento'."
            )

        return values