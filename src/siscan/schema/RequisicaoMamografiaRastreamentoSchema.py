from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field
from pydantic.functional_validators import model_validator

from src.siscan.schema.RequisicaoMamografiaSchema import RequisicaoMamografiaSchema

from src.siscan.schema import TipoDeMamografia


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

    @model_validator(mode="after")
    def valida_regras_condicionais(cls, values):
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
                "tipo_mamografia_de_rastreamento": "01",
                "data_da_solicitacao": "18/06/2025",
            }
        }
    }
