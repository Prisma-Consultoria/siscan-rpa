from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


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
            json_schema_extra={"x-widget": "text"},
            max_length=15,
            min_length=15,
            title="Cartão SUS",
        ),
    ]
    cpf: Annotated[
        Optional[str],
        Field(
            description="CPF do paciente (apenas números, 11 dígitos) - opcional",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{11}$",
            title="CPF",
        ),
    ] = None
    nome: Annotated[
        str,
        Field(
            description="Nome completo do paciente",
            json_schema_extra={"x-widget": "text"},
            min_length=1,
            title="Nome",
        ),
    ]
    nome_da_mae: Annotated[
        str,
        Field(
            description="Nome completo da mãe do paciente",
            json_schema_extra={"x-widget": "text"},
            min_length=1,
            title="Nome da Mãe",
        ),
    ]
    data_de_nascimento: Annotated[
        str,
        Field(
            description="Data de nascimento no formato DD/MM/AAAA",
            json_schema_extra={"x-widget": "date"},
            pattern="^\\d{2}/\\d{2}/\\d{4}$",
            title="Data de Nascimento",
        ),
    ]
    nacionalidade: Annotated[
        str,
        Field(
            description="Nacionalidade do paciente",
            json_schema_extra={"x-widget": "select"},
            title="Nacionalidade",
        ),
    ]
    sexo: Annotated[
        Sexo,
        Field(
            description="Sexo biológico do paciente (M=Masculino, F=Feminino)",
            json_schema_extra={"x-widget": "checkbox"},
            title="Sexo",
        ),
    ]
    raca_cor: Annotated[
        str,
        Field(
            description="Raça/Cor declarada pelo paciente",
            json_schema_extra={"x-widget": "text"},
            title="Raça/Cor",
        ),
    ]
    uf: Annotated[
        str,
        Field(
            description="Unidade Federativa (UF) com 2 letras",
            json_schema_extra={"x-widget": "text"},
            max_length=2,
            min_length=2,
            title="UF",
        ),
    ]
    municipio: Annotated[
        str,
        Field(
            description="Nome do município de residência",
            json_schema_extra={"x-widget": "text"},
            title="Município",
        ),
    ]
    tipo_logradouro: Annotated[
        str,
        Field(
            description="Tipo de logradouro (ex: Rua, Avenida)",
            json_schema_extra={"x-widget": "text"},
            title="Tipo Logradouro",
        ),
    ]
    nome_logradouro: Annotated[
        str,
        Field(
            description="Nome do logradouro",
            json_schema_extra={"x-widget": "text"},
            title="Nome Logradouro",
        ),
    ]
    numero: Annotated[
        str,
        Field(
            description="Número do endereço",
            json_schema_extra={"x-widget": "text"},
            title="Numero",
        ),
    ]
    bairro: Annotated[
        str,
        Field(
            description="Bairro de residência",
            json_schema_extra={"x-widget": "text"},
            title="Bairro",
        ),
    ]
    cep: Annotated[
        str,
        Field(
            description="CEP (apenas números, 8 dígitos)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{8}$",
            title="Cep",
        ),
    ]
    apelido: Annotated[
        Optional[str],
        Field(
            description="Apelido do paciente (opcional)",
            json_schema_extra={"x-widget": "text"},
            title="Apelido",
        ),
    ] = None
    escolaridade: Annotated[
        Optional[Escolaridade],
        Field(
            description="Nível de escolaridade (0=Selecione, 1=Analfabeto, 2=Ensino Fundamental Incompleto, 3=Ensino Fundamental Completo, 4=Ensino Médio Completo, 5=Ensino Superior Completo)",
            json_schema_extra={"x-widget": "select"},
            title="Escolaridade:",
        ),
    ] = None
    ponto_de_referencia: Annotated[
        Optional[str],
        Field(
            description="Ponto de referência (opcional)",
            json_schema_extra={"x-widget": "text"},
            title="Ponto de Referência",
        ),
    ] = None
    tipo_exame_mama: Annotated[
        Optional[TipoExameMama],
        Field(
            description='Tipo de exame de mama: 01=Mamografia, 03=Cito de Mama, 05=Histo de Mama',
            json_schema_extra={'x-widget': 'radio'},
            title='Mama',
        ),
    ] = None
    unidade_requisitante: Annotated[
        str,
        Field(
            description="CNES da unidade requisitante",
            json_schema_extra={"x-widget": "select"},
            title="Unidade Requisitante",
        ),
    ]
    prestador: Annotated[
        str,
        Field(
            description="Nome do prestador de serviço",
            json_schema_extra={"x-widget": "select"},
            title="Prestador",
        ),
    ]
