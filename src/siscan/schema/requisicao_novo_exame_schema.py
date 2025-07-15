from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Optional


class Sexo(Enum):
    MASCULINO = "M"
    FEMININO = "F"


class Escolaridade(Enum):
    NONE = "0"
    ANALFABETO = "1"
    ENSINO_FUNDAMENTAL_INCOMPLETO = "2"
    ENSINO_FUNDAMENTAL_COMPLETO = "3"
    ENSINO_MEDIO_COMPLETO = "4"
    ENSINO_SUPERIOR_COMPLETO = "5"


class TipoExameMama(Enum):
    MAMOGRAFIA = "01"
    CITO_DE_MAMA = "03"
    HISTO_DE_MAMA = "05"


class RequisicaoNovoExameSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    cartao_sus: Annotated[
        str,
        Field(
            description="Número do Cartão SUS (15 dígitos)",
            json_schema_extra={"x-widget": "text", "x-xpath": ""},
            max_length=15,
            min_length=15,
            title="Cartão SUS",
        ),
    ]
    apelido: Annotated[
        Optional[str],
        Field(
            description="Apelido do paciente (opcional)",
            json_schema_extra={"x-widget": "text", "x-xpath": ""},
            title="Apelido",
        ),
    ] = None
    escolaridade: Annotated[
        Optional[Escolaridade],
        Field(
            description="Nível de escolaridade (0=Selecione, 1=Analfabeto, 2=Ensino Fundamental Incompleto, 3=Ensino Fundamental Completo, 4=Ensino Médio Completo, 5=Ensino Superior Completo)",
            json_schema_extra={"x-widget": "select", "x-xpath": ""},
            title="Escolaridade:",
        ),
    ] = None
    ponto_de_referencia: Annotated[
        Optional[str],
        Field(
            description="Ponto de referência (opcional)",
            json_schema_extra={"x-widget": "text", "x-xpath": ""},
            title="Ponto de Referência",
        ),
    ] = None
    tipo_exame_mama: Annotated[
        Optional[TipoExameMama],
        Field(
            description="Tipo de exame de mama: 01=Mamografia, 03=Cito de Mama, 05=Histo de Mama",
            json_schema_extra={"x-widget": "radio", "x-xpath": ""},
            title="Mama",
        ),
    ] = None
    cnes_unidade_requisitante: Annotated[
        str,
        Field(
            description="CNES da unidade requisitante",
            json_schema_extra={
                "x-widget": "select",
                "x-xpath": "//select[@name='frm:unidadeSaudeCoordenacaoMunicipal']"
            },
            title="Unidade Requisitante",
        ),
    ]
    prestador: Annotated[
        str,
        Field(
            description="Nome do prestador de serviço",
            json_schema_extra={
                "x-widget": "select",
                "x-xpath": "//select[@name='frm:prestadorServicoCoordenacaoMunicipal']"
            },
            title="Prestador",
        ),
    ]
