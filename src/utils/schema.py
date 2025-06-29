import json
from pathlib import Path
from typing import Any, Optional, List, Literal, Annotated
from pydantic import BaseModel, Field, create_model
from enum import Enum


class InputType(Enum):
    """
    # Exemplo de uso
    tipo = LogicalInputType.CHECKBOX
    print(tipo.html_element)  # 'input'
    """

    TEXT = "text"
    DATE = "date"
    VALUE = "value"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    LIST = "list"
    SELECT = "select"
    RADIO = "radio"

    @property
    def html_element(self) -> str:
        if self in {
            InputType.TEXT,
            InputType.DATE,
            InputType.VALUE,
            InputType.NUMBER,
            InputType.CHECKBOX,
        }:
            return "input"
        elif self == InputType.TEXTAREA:
            return "textarea"
        elif self in {InputType.LIST, InputType.SELECT}:
            return "select"
        elif self == InputType.RADIO:
            return "radio"
        else:
            raise ValueError(f"Tipo de input não suportado: {self.value}")


class RequirementLevel(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"

    # Ou, para uso de instância:
    def is_required(self) -> bool:
        """
        Verifica se a instância representa o nível 'required'.
        """
        return self is RequirementLevel.REQUIRED


from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    """Modelo de entrada para login/cadastro de usuário."""

    username: str = Field(..., description="Nome de usuário para cadastro")
    password: str = Field(..., description="Senha do usuário, deve ser criptografada")

    model_config = {
        "json_schema_extra": {"example": {"username": "alice", "password": "secret"}}
    }


class PreencherSolicitacaoInput(BaseModel):
    """Modelo de entrada para preencher solicitação de mamografia."""

    cartao_sus: str
    nome: str
    apelido: str
    data_de_nascimento: str
    nacionalidade: str
    sexo: str
    nome_da_mae: str
    raca_cor: str
    escolaridade: str
    uf: str
    municipio: str
    tipo_logradouro: str
    nome_logradouro: str
    numero: str
    bairro: str
    cep: str
    ponto_de_referencia: str
    unidade_requisitante: str
    prestador: str
    num_prontuario: str
    tem_nodulo_ou_caroco_na_mama: List[str]
    apresenta_risco_elevado_para_cancer_mama: str
    fez_mamografia_alguma_vez: str
    ano_que_fez_a_ultima_mamografia: str
    antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional: str
    fez_radioterapia_na_mama_ou_no_plastrao: str
    radioterapia_localizacao: str
    ano_da_radioterapia_direita: str
    ano_da_radioterapia_esquerda: str
    fez_cirurgia_de_mama: str
    ano_biopsia_cirurgica_incisional_direita: str
    ano_biopsia_cirurgica_incisional_esquerda: str
    ano_biopsia_cirurgica_excisional_direita: str
    ano_biopsia_cirurgica_excisional_esquerda: str
    ano_segmentectomia_direita: str
    ano_segmentectomia_esquerda: str
    ano_centralectomia_direita: str
    ano_centralectomia_esquerda: str
    ano_dutectomia_direita: str
    ano_dutectomia_esquerda: str
    ano_mastectomia_direita: str
    ano_mastectomia_esquerda: str
    ano_mastectomia_poupadora_pele_direita: str
    ano_mastectomia_poupadora_pele_esquerda: str
    ano_mastectomia_poupadora_pele_complexo_papilar_direita: str
    ano_mastectomia_poupadora_pele_complexo_papilar_esquerda: str
    ano_linfadenectomia_axilar_direita: str
    ano_linfadenectomia_axilar_esquerda: str
    ano_biopsia_linfonodo_sentinela_direita: str
    ano_biopsia_linfonodo_sentinela_esquerda: str
    ano_reconstrucao_mamaria_direita: str
    ano_reconstrucao_mamaria_esquerda: str
    ano_mastoplastia_redutora_direita: str
    ano_mastoplastia_redutora_esquerda: str
    ano_inclusao_implantes_direita: str
    ano_inclusao_implantes_esquerda: str
    mamografia_de_rastreamento: str
    data_da_solicitacao: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "cartao_sus": "768075541110002",
                "nome": "FRANSCISCA CHICA MARIA BUNITA",
                "apelido": "MARIA BUNITA",
                "data_de_nascimento": "11/01/1974",
                "nacionalidade": "BRASILEIRO",
                "sexo": "F",
                "nome_da_mae": "RAPUNZEL OLIVEIRA DOS CONFINS",
                "raca_cor": "BRANCA",
                "escolaridade": "4",
                "uf": "PR",
                "municipio": "CURITIBA",
                "tipo_logradouro": "RUA",
                "nome_logradouro": "PROFESSOR GUIDO STRAUBE",
                "numero": "1052",
                "bairro": "VILA IZABEL",
                "cep": "80320030",
                "ponto_de_referencia": "PONTO DE REFERÊNCIA",
                "unidade_requisitante": "0274267",
                "prestador": "HOSPITAL ERASTO GAERTNER",
                "num_prontuario": "123456789",
                "tem_nodulo_ou_caroco_na_mama": ["01", "02"],
                "apresenta_risco_elevado_para_cancer_mama": "01",
                "fez_mamografia_alguma_vez": "01",
                "ano_que_fez_a_ultima_mamografia": "2025",
                "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional": "03",
                "fez_radioterapia_na_mama_ou_no_plastrao": "01",
                "radioterapia_localizacao": "03",
                "ano_da_radioterapia_direita": "2023",
                "ano_da_radioterapia_esquerda": "2023",
                "fez_cirurgia_de_mama": "01",
                "ano_biopsia_cirurgica_incisional_direita": "2000",
                "ano_biopsia_cirurgica_incisional_esquerda": "2001",
                "ano_biopsia_cirurgica_excisional_direita": "2002",
                "ano_biopsia_cirurgica_excisional_esquerda": "2003",
                "ano_segmentectomia_direita": "2004",
                "ano_segmentectomia_esquerda": "2005",
                "ano_centralectomia_direita": "2006",
                "ano_centralectomia_esquerda": "2007",
                "ano_dutectomia_direita": "2008",
                "ano_dutectomia_esquerda": "2009",
                "ano_mastectomia_direita": "2010",
                "ano_mastectomia_esquerda": "2011",
                "ano_mastectomia_poupadora_pele_direita": "2012",
                "ano_mastectomia_poupadora_pele_esquerda": "2013",
                "ano_mastectomia_poupadora_pele_complexo_papilar_direita": "2014",
                "ano_mastectomia_poupadora_pele_complexo_papilar_esquerda": "2015",
                "ano_linfadenectomia_axilar_direita": "2016",
                "ano_linfadenectomia_axilar_esquerda": "2017",
                "ano_biopsia_linfonodo_sentinela_direita": "2018",
                "ano_biopsia_linfonodo_sentinela_esquerda": "2019",
                "ano_reconstrucao_mamaria_direita": "2020",
                "ano_reconstrucao_mamaria_esquerda": "2021",
                "ano_mastoplastia_redutora_direita": "2022",
                "ano_mastoplastia_redutora_esquerda": "2023",
                "ano_inclusao_implantes_direita": "2024",
                "ano_inclusao_implantes_esquerda": "2025",
                "mamografia_de_rastreamento": "01",
                "data_da_solicitacao": "18/06/2025",
            }
        }
    }


def _parse_field(fs: dict, required: bool):
    t = fs.get("type")
    optional = False
    if isinstance(t, list):
        optional = "null" in t
        t = [x for x in t if x != "null"]
        t = t[0] if t else None
    default = ... if required and not optional else None

    if t == "string":
        typ = str
        if "enum" in fs:
            typ = Literal[tuple(v for v in fs["enum"] if v is not None)]
        kwargs = {}
        if "pattern" in fs:
            kwargs["pattern"] = fs["pattern"]
        if "minLength" in fs:
            kwargs["min_length"] = fs["minLength"]
        if "maxLength" in fs:
            kwargs["max_length"] = fs["maxLength"]
        return (Optional[typ] if optional else typ, Field(default, **kwargs))
    if t == "array":
        items = fs.get("items", {})
        item_type = str
        if "enum" in items:
            item_type = Literal[tuple(v for v in items["enum"] if v is not None)]
        kwargs = {}
        if "minItems" in fs:
            kwargs["min_length"] = fs["minItems"]
        if "maxItems" in fs:
            kwargs["max_length"] = fs["maxItems"]
        typ = List[item_type]
        return (Optional[typ] if optional else typ, Field(default, **kwargs))

    return (Optional[Any] if optional else Any, Field(default))


def create_model_from_json_schema(name: str, schema_path: Path) -> type[BaseModel]:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    required = schema.get("required", [])
    fields = {}
    for fname, fs in props.items():
        ftype, field = _parse_field(fs, fname in required)
        fields[fname] = (ftype, field)

    model = create_model(name, **fields)
    model.__schema__ = schema
    model.__schema_path__ = str(schema_path)
    return model


# Cria modelo para requisicao mamografia
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "siscan" / "schemas"
MAMO_SCHEMA_PATH = SCHEMA_DIR / "requisicao_exame_mamografia_rastreamento.schema.json"
MamografiaRequest = create_model_from_json_schema("MamografiaRequest", MAMO_SCHEMA_PATH)
