from __future__ import annotations

from enum import Enum
from typing import Annotated, List, Optional

from pydantic import Field
from pydantic.functional_validators import model_validator
from src.siscan.schema.RequisicaoNovoExameSchema import RequisicaoNovoExameSchema


class TemNoduloOuCarocoNaMama(Enum):
    SIM_MAMA_DIREITA = "01"
    SIM_MAMA_ESQUERDA = "02"
    NAO = "04"


class YNIDK(Enum):
    SIM = "01"
    NAO = "02"
    NAO_SABE = "03"


class Lateralidade(Enum):
    DIREITA = "01"
    ESQUERDA = "02"
    AMBAS = "03"


class YN(Enum):
    SIM = "01"
    NAO = "02"


class TipoDeMamografia(Enum):
    DIAGNOSTICA = "Diagnóstica"
    RASTREAMENTO = "Rastreamento"


class TipoMamografiaRastreamento(Enum):
    POPULACAO_ALVO = "01"
    RISCO_ELEVADO_FAMILIAR = "02"
    CANCER_PREVIO = "03"


class RequisicaoMamografiaRastreamentoSchema(RequisicaoNovoExameSchema):
    num_prontuario: Annotated[
        str,
        Field(
            description="Número do prontuário do paciente",
            json_schema_extra={"x-widget": "text"},
            title="Nº do Prontuário",
        ),
    ]
    tem_nodulo_ou_caroco_na_mama: Annotated[
        List[TemNoduloOuCarocoNaMama],
        Field(
            description="Presença de nódulo ou caroço na mama: 01=Sim Mama Direita, 02=Sim Mama Esquerda, 04=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="TEM NÓDULO OU CAROÇO NA MAMA?",
        ),
    ]
    apresenta_risco_elevado_para_cancer_mama: Annotated[
        YNIDK,
        Field(
            description="Risco elevado para câncer de mama: 01=Sim, 02=Não, 03=Não sabe",
            json_schema_extra={"x-widget": "radio"},
            title="APRESENTA RISCO ELEVADO PARA CÂNCER DE MAMA?",
        ),
    ]
    antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional: Annotated[
        YNIDK,
        Field(
            description="As mamas já foram examinadas por profissional: 01=Sim, 02=Nunca, 03=Não sabe",
            json_schema_extra={"x-widget": "radio"},
            title="ANTES DESTA CONSULTA, TEVE AS MAMAS EXAMINADAS POR UM PROFISSIONAL DE SAÚDE?",
        ),
    ]
    fez_mamografia_alguma_vez: Annotated[
        YNIDK,
        Field(
            description="Já fez mamografia alguma vez: 01=Sim, 02=Não, 03=Não sabe",
            json_schema_extra={"x-widget": "radio"},
            title="FEZ MAMOGRAFIA ALGUMA VEZ?",
        ),
    ]
    ano_que_fez_a_ultima_mamografia: Annotated[
        Optional[str],
        Field(
            description="Ano da última mamografia (AAAA)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="QUANDO FEZ A ÚLTIMA MAMOGRAFIA?",
        ),
    ] = None
    fez_radioterapia_na_mama_ou_no_plastrao: Annotated[
        YNIDK,
        Field(
            description="Fez radioterapia na mama ou plastrão: 01=Sim, 02=Não, 03=Não sabe",
            json_schema_extra={"x-widget": "radio"},
            title="FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?",
        ),
    ]
    radioterapia_localizacao: Annotated[
        Optional[Lateralidade],
        Field(
            description="Localização da radioterapia: 01=Esquerda, 02=Direita, 03=Ambas",
            json_schema_extra={"x-widget": "radio"},
            title="RADIOTERAPIA - LOCALIZAÇÃO",
        ),
    ] = None
    ano_da_radioterapia_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da radioterapia - mama direita (AAAA)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="ANO DA RADIOTERAPIA - DIREITA",
        ),
    ] = None
    ano_da_radioterapia_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da radioterapia - mama esquerda (AAAA)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="ANO DA RADIOTERAPIA - ESQUERDA",
        ),
    ] = None
    fez_cirurgia_de_mama: Annotated[
        YN,
        Field(
            description="Fez cirurgia de mama: 01=Sim, 02=Não",
            json_schema_extra={"x-widget": "radio"},
            title="FEZ CIRURGIA DE MAMA?",
        ),
    ]
    ano_biopsia_cirurgica_incisional_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia cirúrgica incisional (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia cirúrgica incisional (Direita)",
        ),
    ] = None
    ano_biopsia_cirurgica_incisional_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia cirúrgica incisional (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia cirúrgica incisional (Esquerda)",
        ),
    ] = None
    ano_biopsia_cirurgica_excisional_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia cirúrgica excisional (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia cirúrgica excisional (Direita)",
        ),
    ] = None
    ano_biopsia_cirurgica_excisional_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia cirúrgica excisional (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia cirúrgica excisional (Esquerda)",
        ),
    ] = None
    ano_segmentectomia_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da segmentectomia (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Segmentectomia (Direita)",
        ),
    ] = None
    ano_segmentectomia_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da segmentectomia (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Segmentectomia (Esquerda)",
        ),
    ] = None
    ano_centralectomia_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da centralectomia (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Centralectomia (Direita)",
        ),
    ] = None
    ano_centralectomia_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da centralectomia (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Centralectomia (Esquerda)",
        ),
    ] = None
    ano_dutectomia_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da dutectomia (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Dutectomia (Direita)",
        ),
    ] = None
    ano_dutectomia_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da dutectomia (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Dutectomia (Esquerda)",
        ),
    ] = None
    ano_mastectomia_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia (Direita)",
        ),
    ] = None
    ano_mastectomia_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia (Esquerda)",
        ),
    ] = None
    ano_mastectomia_poupadora_pele_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia poupadora de pele (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia poupadora de pele (Direita)",
        ),
    ] = None
    ano_mastectomia_poupadora_pele_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia poupadora de pele (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia poupadora de pele (Esquerda)",
        ),
    ] = None
    ano_mastectomia_poupadora_pele_complexo_papilar_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia poupadora de pele e complexo aréolo papilar (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia poupadora de pele e complexo aréolo papilar (Direita)",
        ),
    ] = None
    ano_mastectomia_poupadora_pele_complexo_papilar_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da mastectomia poupadora de pele e complexo aréolo papilar (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastectomia poupadora de pele e complexo aréolo papilar (Esquerda)",
        ),
    ] = None
    ano_linfadenectomia_axilar_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da linfadenectomia axilar (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Linfadenectomia axilar (Direita)",
        ),
    ] = None
    ano_linfadenectomia_axilar_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da linfadenectomia axilar (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Linfadenectomia axilar (Esquerda)",
        ),
    ] = None
    ano_biopsia_linfonodo_sentinela_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia de linfonodo sentinela (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia de linfonodo sentinela (Direita)",
        ),
    ] = None
    ano_biopsia_linfonodo_sentinela_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da biópsia de linfonodo sentinela (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Biópsia de linfonodo sentinela (Esquerda)",
        ),
    ] = None
    ano_reconstrucao_mamaria_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da reconstrução mamária (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Reconstrução mamária (Direita)",
        ),
    ] = None
    ano_reconstrucao_mamaria_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da reconstrução mamária (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Reconstrução mamária (Esquerda)",
        ),
    ] = None
    ano_mastoplastia_redutora_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da mastoplastia redutora (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastoplastia redutora (Direita)",
        ),
    ] = None
    ano_mastoplastia_redutora_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da mastoplastia redutora (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Mastoplastia redutora (Esquerda)",
        ),
    ] = None
    ano_inclusao_implantes_direita: Annotated[
        Optional[str],
        Field(
            description="Ano da inclusão de implantes (direita)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Inclusão de implantes (Direita)",
        ),
    ] = None
    ano_inclusao_implantes_esquerda: Annotated[
        Optional[str],
        Field(
            description="Ano da inclusão de implantes (esquerda)",
            json_schema_extra={"x-widget": "text"},
            pattern="^\\d{4}$",
            title="Inclusão de implantes (Esquerda)",
        ),
    ] = None
    tipo_de_mamografia: Annotated[
        TipoDeMamografia,
        Field(
            description="Tipo de mamografia: 01=Diagnóstica, 02=Rastreamento",
            json_schema_extra={"x-widget": "radio"},
            title="TIPO DE MAMOGRAFIA",
        ),
    ]
    mamografia_de_rastreamento: Annotated[
        Optional[TipoMamografiaRastreamento],
        Field(
            description="Indicação da mamografia de rastreamento: 01=População alvo, 02=Risco elevado, 03=Paciente já tratado",
            json_schema_extra={"x-widget": "radio"},
            title="MAMOGRAFIA DE RASTREAMENTO",
        ),
    ] = None
    data_da_solicitacao: Annotated[
        Optional[str],
        Field(
            description="Data da solicitação do exame no formato DD/MM/AAAA",
            json_schema_extra={"x-widget": "date"},
            pattern="^\\d{2}/\\d{2}/\\d{4}$",
            title="Data da Solicitação",
        ),
    ] = None

    @model_validator(mode="after")
    def valida_regras_condicionais(cls, values):
        # 1) Se existe '04' em tem_nodulo_ou_caroco_na_mama, então só pode haver esse item
        nodulos = values.tem_nodulo_ou_caroco_na_mama or []
        if any(n.value == "04" for n in nodulos):
            if len(nodulos) != 1 or nodulos[0].value != "04":
                raise ValueError(
                    "Quando 'tem_nodulo_ou_caroco_na_mama' contém '04', "
                    "deve ser exatamente ['04']."
                )

        # 2) Se fez_mamografia_alguma_vez == '01', ano_que_fez_a_ultima_mamografia é obrigatório
        fez = values.fez_mamografia_alguma_vez
        ano_ultima = values.ano_que_fez_a_ultima_mamografia
        if fez == YNIDK.SIM and not ano_ultima:
            raise ValueError(
                "Se fez mamografia (01), precisa informar 'ano_que_fez_a_ultima_mamografia'."
            )
        # E se não fez, não deve informar:
        if fez != YNIDK.SIM and ano_ultima:
            raise ValueError(
                "Se não fez mamografia (≠01), não deve informar 'ano_que_fez_a_ultima_mamografia'."
            )

        # 3) Se fez_radioterapia_na_mama_ou_no_plastrao == '01', radioterapia_localizacao é obrigatório
        fez_radio = values.fez_radioterapia_na_mama_ou_no_plastrao
        loc = values.radioterapia_localizacao
        if fez_radio == YNIDK.SIM and not loc:
            raise ValueError(
                "Se fez radioterapia (01), precisa informar 'radioterapia_localizacao'."
            )
        if fez_radio != YNIDK.SIM and loc:
            raise ValueError(
                "Se não fez radioterapia (≠01), não deve informar 'radioterapia_localizacao'."
            )

        # 4) Dependências dentro de radioterapia_localizacao
        if loc == Lateralidade.ESQUERDA and not values.ano_da_radioterapia_direita:
            raise ValueError(
                "Se 'radioterapia_localizacao' = 02, precisa 'ano_da_radioterapia_direita'."
            )
        if loc == Lateralidade.DIREITA and not values.ano_da_radioterapia_esquerda:
            raise ValueError(
                "Se 'radioterapia_localizacao' = 01, precisa 'ano_da_radioterapia_esquerda'."
            )
        if loc == Lateralidade.AMBAS:
            if (
                not values.ano_da_radioterapia_direita
                or not values.ano_da_radioterapia_esquerda
            ):
                raise ValueError(
                    "Se 'radioterapia_localizacao' = 03, precisa informar ambos "
                    "'ano_da_radioterapia_direita' e 'ano_da_radioterapia_esquerda'."
                )

        # 5) Se tipo_de_mamografia == 'Rastreamento', mamografia_de_rastreamento é obrigatório
        tipo = values.tipo_de_mamografia
        mamo = values.mamografia_de_rastreamento
        if tipo == TipoDeMamografia.RASTREAMENTO and not mamo:
            raise ValueError(
                "Se tipo_de_mamografia = Rastreamento, precisa informar 'mamografia_de_rastreamento'."
            )
        if tipo != TipoDeMamografia.RASTREAMENTO and mamo:
            raise ValueError(
                "Se tipo_de_mamografia ≠ Rastreamento, não deve informar 'mamografia_de_rastreamento'."
            )

        return values
