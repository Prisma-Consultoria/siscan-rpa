from __future__ import annotations

import logging
from enum import Enum
from pydantic import Field
from pydantic.functional_validators import model_validator
from typing import Annotated, Optional, List, ClassVar

from src.siscan.schema import Lateralidade
from src.siscan.schema.requisicao_mamografia_schema import \
    RequisicaoMamografiaSchema

logger = logging.getLogger(__name__)


class YesOrNone(Enum):
    SIM = "S"
    NONE = "null"


class TipoDescargaPapilar(Enum):
    CRISTALINA = "01"
    HEMORRAGICA = "02"
    NONE = "null"


class LocalizacaoMama(Enum):
    QSL = "01"      # Quadrante Superior Lateral
    QIL = "02"      # Quadrante Inferior Lateral
    QSM = "03"      # Quadrante Superior Medial
    QIM = "04"      # Quadrante Inferior Medial
    UQlat = "05"    # União dos quadrantes laterais
    UQsup = "06"    # União dos quadrantes superiores
    UQmed = "07"    # União dos quadrantes medianos
    UQinf = "08"    # União dos quadrantes inferiores
    RRA = "09"      # Região Retroareolar
    PA = "10"       # Prolongamento axilar


class LocalizacaoLinfonodo(Enum):
    AXILAR = "01"
    SUPRACLAVICULAR = "02"


class RequisicaoMamografiaDiagnosticaSchema(RequisicaoMamografiaSchema):
    XPATH_DIV_MAMA_DIREITA: ClassVar[str] = "//div[@id='frm:mamaDireita']"
    XPATH_DIV_MAMA_ESQUERDA: ClassVar[str] = "//div[@id='frm:mamaEsquerda']"

    # Constante de classe: campos do grupo 'achados ao exame clínico'
    FIELDS_ACHADOS_EXAME_CLINICO: ClassVar[list] = [
        "exame_clinico_mama_direita_lesao_papilar",
        "exame_clinico_mama_direita_descarga_papilar_espontanea",
        "exame_clinico_mama_direita_nodulo_localizacao",
        "exame_clinico_mama_direita_espessamento_localizacao",
        "exame_clinico_mama_direita_linfonodo_palpavel",
        "exame_clinico_mama_esquerda_lesao_papilar",
        "exame_clinico_mama_esquerda_descarga_papilar_espontanea",
        "exame_clinico_mama_esquerda_nodulo_localizacao",
        "exame_clinico_mama_esquerda_espessamento_localizacao",
        "exame_clinico_mama_esquerda_linfonodo_palpavel",
    ]

    # Constante de classe: campos do grupo 'controle radiológico de lesão
    # categoria 3'
    FIELDS_CONTROLE_RADIOLOGICO: ClassVar[list] = [
        "controle_radiologico_lesao_categoria_3_mama_direita_nodulo",
        "controle_radiologico_lesao_categoria_3_mama_direita_microcalcificacoes",
        "controle_radiologico_lesao_categoria_3_mama_direita_assimetria_focal",
        "controle_radiologico_lesao_categoria_3_mama_direita_assimetria_difusa",
        "controle_radiologico_lesao_categoria_3_mama_direita_area_densa",
        "controle_radiologico_lesao_categoria_3_mama_direita_distorcao_focal",
        "controle_radiologico_lesao_categoria_3_mama_direita_linfonodo_axilar",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_nodulo",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_microcalcificacoes",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_focal",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_difusa",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_area_densa",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_distorcao_focal",
        "controle_radiologico_lesao_categoria_3_mama_esquerda_linfonodo_axilar",
    ]

    # Constante de classe: campos do grupo 'lesão diagnóstico de câncer'
    FIELDS_LESAO_CANCER: ClassVar[list] = [
        "lesao_diagnostico_cancer_mama_direita_nodulo",
        "lesao_diagnostico_cancer_mama_direita_microcalcificacoes",
        "lesao_diagnostico_cancer_mama_direita_assimetria_focal",
        "lesao_diagnostico_cancer_mama_direita_assimetria_difusa",
        "lesao_diagnostico_cancer_mama_direita_area_densa",
        "lesao_diagnostico_cancer_mama_direita_distorcao_focal",
        "lesao_diagnostico_cancer_mama_direita_linfonodo_axilar",
        "lesao_diagnostico_cancer_mama_esquerda_nodulo",
        "lesao_diagnostico_cancer_mama_esquerda_microcalcificacoes",
        "lesao_diagnostico_cancer_mama_esquerda_assimetria_focal",
        "lesao_diagnostico_cancer_mama_esquerda_assimetria_difusa",
        "lesao_diagnostico_cancer_mama_esquerda_area_densa",
        "lesao_diagnostico_cancer_mama_esquerda_distorcao_focal",
        "lesao_diagnostico_cancer_mama_esquerda_linfonodo_axilar",
    ]

    # Constante de classe: campos do grupo 'revisão mamografia outra
    # instituição'
    FIELDS_REVISAO_MAMOGRAFIA: ClassVar[list] = [
        "revisao_mamografia_outra_instituicao_mama_direita_categoria_0",
        "revisao_mamografia_outra_instituicao_mama_direita_categoria_3",
        "revisao_mamografia_outra_instituicao_mama_direita_categoria_4",
        "revisao_mamografia_outra_instituicao_mama_direita_categoria_5",
        "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0",
        "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3",
        "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4",
        "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5",
    ]

    # Constante de classe: campos do grupo 'avaliação resposta quimioterapia'
    FIELDS_CONTROLE_PAAF: ClassVar[list] = [
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_nodulo",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_microcalcificacoes",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_focal",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_difusa",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_area_densa",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_distorcao_focal",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_linfonodo_axilar",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_nodulo",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_microcalcificacoes",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_focal",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_difusa",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_area_densa",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_distorcao_focal",
        "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_linfonodo_axilar",
    ]

    # Achados no exame clínico
    # Mamografia realizada nas mulheres com sinal e sintoma de câncer de mama
    # (os sinais e sintomas contemplados no formulário são: lesão papilar,
    # descarga papilar espontânea, nódulo, espessamento e linfonodo axilar e
    # supraclavicular)
    achados_exame_clinico: Annotated[
        bool,
        Field(
            description="Achados no exame clínico: True=Sim, False=Não",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:achadosExameClinico']"
            },
            title="ACHADOS NO EXAME CLÍNICO",
        ),
    ] = False
    # MAMA DIREITA
    exame_clinico_mama_direita_lesao_papilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Exame clínico da mama direita: Lesão papilar (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:lesaoPapilarDireita']"
            },
            title="MAMA DIREITA - LESÃO PAPILAR",
        ),
    ] = None
    exame_clinico_mama_direita_descarga_papilar_espontanea: Annotated[
        Optional[TipoDescargaPapilar],
        Field(
            description="Exame clínico da mama direita: Tipo de descarga papilar (01=Cristalina, 02=Hemorrágica)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_DIREITA}//fieldset[legend[text()='DESCARGA PAPILAR ESPONTÂNEA']]"
            },
            title="MAMA DIREITA - DESCARGA PAPILAR ESPONTÂNEA",
        ),
    ] = None
    exame_clinico_mama_direita_nodulo_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama direita: Localização do nódulo (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_DIREITA}//fieldset[legend[text()='NÓDULO - LOCALIZAÇÃO']]"
            },
            title="MAMA DIREITA - NÓDULO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_direita_espessamento_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama direita: Localização do espessamento (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_DIREITA}//fieldset[legend[text()='ESPESSAMENTO - LOCALIZAÇÃO']]"
            },
            title="MAMA DIREITA - ESPESSAMENTO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_direita_linfonodo_palpavel: Annotated[
        Optional[List[LocalizacaoLinfonodo]],
        Field(
            description="Exame clínico da mama direita: Linfonodo palpável (01=Axilar, 02=Supraclavicular)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_DIREITA}//fieldset[legend[text()='LINFONODO PALPÁVEL']]"
            },
            title="MAMA DIREITA - LINFONODO PALPÁVEL",
        )
    ] = None
    # MAMA ESQUERDA
    exame_clinico_mama_esquerda_lesao_papilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Exame clínico da mama esquerda: Lesão papilar (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:lesaoPapilarEsquerda']"},
            title="MAMA ESQUERDA - LESÃO PAPILAR",
        ),
    ] = None
    exame_clinico_mama_esquerda_descarga_papilar_espontanea: Annotated[
        Optional[TipoDescargaPapilar],
        Field(
            description="Exame clínico da mama esquerda: Tipo de descarga papilar (01=Cristalina, 02=Hemorrágica)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_ESQUERDA}//fieldset[legend[text()='DESCARGA PAPILAR ESPONTÂNEA']]"
            },
            title="MAMA ESQUERDA - DESCARGA PAPILAR ESPONTÂNEA",
        ),
    ] = None
    exame_clinico_mama_esquerda_nodulo_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama esquerda: Localização do nódulo (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_ESQUERDA}//fieldset[legend[text()='NÓDULO - LOCALIZAÇÃO']]"
            },
            title="MAMA ESQUERDA - NÓDULO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_esquerda_espessamento_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama esquerda: Localização do espessamento (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_ESQUERDA}//fieldset[legend[text()='ESPESSAMENTO - LOCALIZAÇÃO']]"
            },
            title="MAMA ESQUERDA - ESPESSAMENTO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_esquerda_linfonodo_palpavel: Annotated[
        Optional[List[LocalizacaoLinfonodo]],
        Field(
            description="Exame clínico da mama esquerda: Linfonodo palpável (01=Axilar, 02=Supraclavicular)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": f"{XPATH_DIV_MAMA_ESQUERDA}//fieldset[legend[text()='LINFONODO PALPÁVEL']]"
            },
            title="MAMA ESQUERDA - LINFONODO PALPÁVEL",
        ),
    ] = None

    # Controle radiológico de lesão Categoria 3 (BI-RADS )
    # Mamografia realizada em paciente com laudo anterior de lesão
    # provavelmente benigna
    controle_radiologico_lesao_categoria_3: Annotated[
        bool,
        Field(
            description="Controle radiológico de lesão categoria 3: True=Sim, False=Não",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleRadiologicoLesao']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3",
        ),
    ] = False
    # MAMA DIREITA
    controle_radiologico_lesao_categoria_3_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Nódulo (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoNoduloDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - NÓDULO",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoMicrocalcificacoesDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAssimetriaFocalDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAssimetriaDifusaDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Área densa (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAreaDensaDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoDistorcaoFocalDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoLinfonodoAxiliarDireita']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    # MAMA ESQUERDA
    controle_radiologico_lesao_categoria_3_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Nódulo (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoNoduloEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoMicrocalcificacoesEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAssimetriaFocalEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAssimetriaDifusaEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Área densa (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoAreaDensaEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoDistorcaoFocalEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:radiologicoLinfonodoAxiliarEsquerda']"
            },
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None

    # Lesão diagnóstico de câncer
    # Mamografia realizada em paciente já com diagnóstico de câncer de mama,
    # por histopatológico, mas antes do tratamento
    lesao_diagnostico_cancer: Annotated[
        bool,
        Field(
            description="Lesão diagnóstico de câncer: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoDiagnosticoCancer']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER",
        ),
    ] = False
    # MAMA DIREITA
    lesao_diagnostico_cancer_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerNoduloDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - NÓDULO",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerMicrocalcificacoesDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAssimetriaFocalDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAssimetriaDifusaDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAreaDensaDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerDistorcaoFocalDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerLinfonodoAxiliarDireita']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    # MAMA ESQUERDA
    lesao_diagnostico_cancer_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerNoduloEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerMicrocalcificacoesEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAssimetriaFocalEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAssimetriaDifusaEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerAreaDensaEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerDistorcaoFocalEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox",
                               "x-xpath": "//input[@name='frm:lesaoCancerLinfonodoAxiliarEsquerda']"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None

    # Avaliação de resposta à quimioterapia neoadjuvante
    # Mamografia realizada após a quimioterapia neoadjuvante, para avaliação
    # da resposta
    avaliacao_resposta_quimioterapia_neoadjuvante: Annotated[
        bool,
        Field(
            description="Avaliação da resposta à quimioterapia neoadjuvante: True=Sim, False=Não",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:avaliacaoRespostaQuimioterapia']"
            },
            title="AVALIAÇÃO DA RESPOSTA À QUIMIOTERAPIA NEADJUVANTE",
        ),
    ] = False
    avaliacao_resposta_quimioterapia_lateralidade: Annotated[
        Optional[Lateralidade],
        Field(
            description="Avaliação da resposta à quimioterapia: Lateralidade (02=Direita, 01=Esquerda, 03=Ambas)",
            json_schema_extra={
                "x-widget": "radio",
                "x-xpath": "//table[@id='frm:avaliacaoRespostaQuimiNeo']"
            },
            title="AVALIAÇÃO DA RESPOSTA À QUIMIOTERAPIA NEOADJUVANTE - LATERALIDADE",
        ),
    ] = None

    # Revisão de mamografia com lesão, realizada em outra instituição
    # Mamografia realizada em paciente com laudo anterior de outra
    # instituição nas categorias 0,3,4 e 5 para revisão de resultado
    revisao_mamografia_outra_instituicao: Annotated[
        bool,
        Field(
            description="Revisão de mamografia em outra instituição: True=Sim, False=Não",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoMamografia']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO",
        ),
    ] = False
    # MAMA DIREITA
    revisao_mamografia_outra_instituicao_mama_direita_categoria_0: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 0 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria0Direita']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 0",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_3: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 3 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria3Direita']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 3",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_4: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 4 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria4Direita']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 4",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_5: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 5 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria5Direita']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 5",
        ),
    ] = None
    # MAMA ESQUERDA
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 0 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria0Esquerda']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 0",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 3 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria3Esquerda']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 3",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 4 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria4Esquerda']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 4",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 5 (S=Sim, None=Não)",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:revisaoCategoria5Esquerda']"
            },
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 5",
        ),
    ] = None

    # Controle de lesão após biópsia ou PAAF com resultado benigno
    # Mamografia realizada em paciente com laudo anterior de biópsia de
    # fragmento ou PAAF de lesões benignas
    controle_lesao_pos_biopsia_paaf_benigna: Annotated[
        bool,
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna: True=Sim, False=Não",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesao']"
            },
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA",
        ),
    ] = False
    # MAMA DIREITA
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Nódulo",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoNoduloDireita']"
            },
            title="... MAMA DIREITA - NÓDULO",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Microcalcificações",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoMicrocalcificacoesDireita']"
            },
            title="... MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Assimetria focal",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAssimetriaFocalDireita']"
            },
            title="... MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Assimetria difusa",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAssimetriaDifusaDireita']"
            },
            title="... MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Área densa",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAreaDensaDireita']"
            },
            title="... MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Distorção focal",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoDistorcaoFocalDireita']"
            },
            title="... MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama direita: Linfonodo axilar",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoLinfonodoAxiliarDireita']"
            },
            title="... MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    # MAMA ESQUERDA
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Nódulo",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoNoduloEsquerda']"
            },
            title="... MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Microcalcificações",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoMicrocalcificacoesEsquerda']"
            },
            title="... MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Assimetria focal",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAssimetriaFocalEsquerda']"
            },
            title="... MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Assimetria difusa",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAssimetriaDifusaEsquerda']"
            },
            title="... MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Área densa",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoAreaDensaEsquerda']"
            },
            title="... MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Distorção focal",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoDistorcaoFocalEsquerda']"
            },
            title="... MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="... mama esquerda: Linfonodo axilar",
            json_schema_extra={
                "x-widget": "checkbox",
                "x-xpath": "//input[@name='frm:controleLesaoLinfonodoAxiliarEsquerda']"
            },
            title="... MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "cartao_sus": "898001160104568",
                "apelido": "",
                "escolaridade": "4",
                "ponto_de_referencia": "PONTO DE REFERÊNCIA",
                "cnes_unidade_requisitante": "0274267",
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

                "exame_clinico_mama_direita_lesao_papilar": "S",
                "exame_clinico_mama_direita_descarga_papilar_espontanea": "01",
                "exame_clinico_mama_direita_nodulo_localizacao": ["01","02","03","04","05","06","07","08","09","10"],
                "exame_clinico_mama_direita_espessamento_localizacao": ["01","02","03","04","05","06","07","08","09","10"],
                "exame_clinico_mama_direita_linfonodo_palpavel": ["01", "02"],
                "exame_clinico_mama_esquerda_lesao_papilar": "S",
                "exame_clinico_mama_esquerda_descarga_papilar_espontanea": "01",
                "exame_clinico_mama_esquerda_nodulo_localizacao": ["01","02","03","04","05","06","07","08","09","10"],
                "exame_clinico_mama_esquerda_espessamento_localizacao": ["01","02","03","04","05","06","07","08","09","10"],
                "exame_clinico_mama_esquerda_linfonodo_palpavel": ["01", "02"],

                "controle_radiologico_lesao_categoria_3_mama_direita_nodulo": None,
                "controle_radiologico_lesao_categoria_3_mama_direita_microcalcificacoes": "S",
                "controle_radiologico_lesao_categoria_3_mama_direita_assimetria_focal": None,
                "controle_radiologico_lesao_categoria_3_mama_direita_assimetria_difusa": "S",
                "controle_radiologico_lesao_categoria_3_mama_direita_area_densa": None,
                "controle_radiologico_lesao_categoria_3_mama_direita_distorcao_focal": "S",
                "controle_radiologico_lesao_categoria_3_mama_direita_linfonodo_axilar": None,
                "controle_radiologico_lesao_categoria_3_mama_esquerda_nodulo": "S",
                "controle_radiologico_lesao_categoria_3_mama_esquerda_microcalcificacoes": None,
                "controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_focal": "S",
                "controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_difusa": None,
                "controle_radiologico_lesao_categoria_3_mama_esquerda_area_densa": "S",
                "controle_radiologico_lesao_categoria_3_mama_esquerda_distorcao_focal": None,
                "controle_radiologico_lesao_categoria_3_mama_esquerda_linfonodo_axilar": "S",

                "lesao_diagnostico_cancer_mama_direita_nodulo": "S",
                "lesao_diagnostico_cancer_mama_direita_microcalcificacoes": None,
                "lesao_diagnostico_cancer_mama_direita_assimetria_focal": "S",
                "lesao_diagnostico_cancer_mama_direita_assimetria_difusa": None,
                "lesao_diagnostico_cancer_mama_direita_area_densa": "S",
                "lesao_diagnostico_cancer_mama_direita_distorcao_focal": None,
                "lesao_diagnostico_cancer_mama_direita_linfonodo_axilar": "S",
                "lesao_diagnostico_cancer_mama_esquerda_nodulo": None,
                "lesao_diagnostico_cancer_mama_esquerda_microcalcificacoes": "S",
                "lesao_diagnostico_cancer_mama_esquerda_assimetria_focal": None,
                "lesao_diagnostico_cancer_mama_esquerda_assimetria_difusa": "S",
                "lesao_diagnostico_cancer_mama_esquerda_area_densa": None,
                "lesao_diagnostico_cancer_mama_esquerda_distorcao_focal": "S",
                "lesao_diagnostico_cancer_mama_esquerda_linfonodo_axilar": None,

                "avaliacao_resposta_quimioterapia_lateralidade": "01",

                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_nodulo": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_microcalcificacoes": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_focal": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_difusa": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_area_densa": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_distorcao_focal": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_direita_linfonodo_axilar": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_nodulo": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_microcalcificacoes": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_focal": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_difusa": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_area_densa": None,
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_distorcao_focal": "S",
                "controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_linfonodo_axilar": None,

                "revisao_mamografia_outra_instituicao_mama_direita_categoria_0": "S",
                "revisao_mamografia_outra_instituicao_mama_direita_categoria_3": None,
                "revisao_mamografia_outra_instituicao_mama_direita_categoria_4": None,
                "revisao_mamografia_outra_instituicao_mama_direita_categoria_5": None,
                "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0": "S",
                "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3": None,
                "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4": None,
                "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5": None,

                "data_da_solicitacao": "18/06/2025",
                "cns_responsavel_coleta": "279802393660002"
            }
        }
    }

    @model_validator(mode="before")
    @classmethod
    def substitui_none_por_str_null(cls, data: dict) -> dict:
        """
        Substitui valores None por YesOrNone.NONE nos campos esperados.
        """
        for field_name in data.keys():
            if data[field_name] is None:
                data[field_name] = "null"
        return data

    @model_validator(mode="after")
    def valida_grupos(cls, values):
        # Início do processo de validação dos grupos semânticos de campos
        logger.debug("Executando valida_grupos ...")

        # === Grupo: Achados ao exame clínico das mamas ===
        # Se qualquer campo deste grupo estiver preenchido, define-se o campo de controle 'achados_exame_clinico' como True
        if any(getattr(values, f) is not None for f in cls.FIELDS_ACHADOS_EXAME_CLINICO):
            values.achados_exame_clinico = True

        # === Grupo: Controle radiológico de lesões categoria BI-RADS 3 ===

        if any(getattr(values, f) is not None for f in cls.FIELDS_CONTROLE_RADIOLOGICO):
            values.controle_radiologico_lesao_categoria_3 = True

        # === Grupo: Lesões com diagnóstico de câncer ===

        if any(getattr(values, f) is not None for f in cls.FIELDS_LESAO_CANCER):
            values.lesao_diagnostico_cancer = True

        # === Grupo: Avaliação da resposta à quimioterapia neoadjuvante ===
        # O preenchimento do campo de lateralidade é suficiente para indicar a existência dessa avaliação
        if values.avaliacao_resposta_quimioterapia_lateralidade is not None:
            values.avaliacao_resposta_quimioterapia_neoadjuvante = True

        # === Grupo: Revisão de mamografia de outra instituição ===
        if any(getattr(values, f) is not None for f in cls.FIELDS_REVISAO_MAMOGRAFIA):
            values.revisao_mamografia_outra_instituicao = True

        # === Grupo: Controle de lesão pós-biópsia (PAFF) benigna ===
        if any(getattr(values, f) is not None for f in cls.FIELDS_CONTROLE_PAAF):
            values.controle_lesao_pos_biopsia_paaf_benigna = True

        # Retorna a instância modificada com os campos de controle atualizados
        return values

    @classmethod
    def _valida_campos_condicionais_ativos(
        cls,
        values: "RequisicaoMamografiaDiagnosticaSchema",
        grupo: str,
        campos_obrigatorios: list[str]
    ) -> None:
        """
        Verifica se os campos de um grupo foram preenchidos quando o grupo está ativo.
        Lança ValueError com descrição esperada se algum campo estiver ausente.
        """
        if getattr(values, grupo, False):
            for field_name in campos_obrigatorios:
                value = getattr(values, field_name)
                field_info = cls.model_fields[field_name]

                # Log para depuração
                logger.debug(f"Campo {field_name}: value={value}, type={type(value)}")

                if value is None:
                    valores_possiveis = cls._extrai_valores_possiveis(field_info.annotation)
                    msg_valores = ", ".join(repr(v) for v in valores_possiveis if v is not None)
                    if None in valores_possiveis:
                        msg_valores += " ou null"
                    raise ValueError(
                        f"O campo '{field_name}' é obrigatório quando '{grupo}' está ativo. "
                        f"Esperado um dos valores: {msg_valores}."
                    )


    @model_validator(mode="after")
    def valida_obrigatoriedade_camopos_condicionais(cls, values):
        logger.debug("Executando valida_obrigatoriedade_camopos_condicionais ...")

        cls._valida_campos_condicionais_ativos(
            values,
            "achados_exame_clinico",
            cls.FIELDS_ACHADOS_EXAME_CLINICO)

        cls._valida_campos_condicionais_ativos(
            values,
            "controle_radiologico_lesao_categoria_3",
            cls.FIELDS_CONTROLE_RADIOLOGICO)

        cls._valida_campos_condicionais_ativos(
            values,
            "lesao_diagnostico_cancer",
            cls.FIELDS_LESAO_CANCER)

        cls._valida_campos_condicionais_ativos(
            values,
            "revisao_mamografia_outra_instituicao",
            cls.FIELDS_REVISAO_MAMOGRAFIA)

        cls._valida_campos_condicionais_ativos(
            values,
            "controle_lesao_pos_biopsia_paaf_benigna",
            cls.FIELDS_CONTROLE_PAAF)

        return values

    @model_validator(mode="after")
    def valida_categoria_revisao_mamografia_unica_por_mama(cls, values):
        """
        Garante que no máximo uma categoria (0, 3, 4 ou 5) esteja marcada como 'S' para cada mama.
        """
        def contar_marcados(campos: list[str]) -> list[str]:
            """Retorna a lista de campos marcados como 'S'."""
            return [campo for campo in campos if getattr(values, campo, None) == YesOrNone.SIM]

        campos_direita = [
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_0",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_3",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_4",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_5",
        ]
        campos_esquerda = [
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5",
        ]

        marcados_direita = contar_marcados(campos_direita)
        marcados_esquerda = contar_marcados(campos_esquerda)

        if len(marcados_direita) > 1:
            raise ValueError(
                f"Apenas um dos campos {campos_direita} pode estar marcado como 'S'. "
                f"Atualmente marcados: {marcados_direita}."
            )

        if len(marcados_esquerda) > 1:
            raise ValueError(
                f"Apenas um dos campos {campos_esquerda} pode estar marcado como 'S'. "
                f"Atualmente marcados: {marcados_esquerda}."
            )
        return values