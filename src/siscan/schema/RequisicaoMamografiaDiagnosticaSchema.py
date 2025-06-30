from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional, List

from pydantic import Field
from pydantic.functional_validators import model_validator

from src.siscan.schema.RequisicaoMamografiaSchema import RequisicaoMamografiaSchema
from src.siscan.schema import Lateralidade


class YesOrNone(Enum):
    SIM = "S"
    NONE = None


class TipoDescargaPapilar(Enum):
    CRISTALINA = "01"
    HEMORRAGICA = "02"


class LocalizacaoMama(Enum):
    QSL = "01"
    QIL = "02"
    QSM = "03"
    QIM = "04"
    UQlat = "05"
    UQsup = "06"
    UQmed = "07"
    UQinf = "08"
    RRA = "09"
    PA = "10"


class LocalizacaoLinfonodo(Enum):
    AXILAR = "01"
    SUPRACLAVICULAR = "02"


class RequisicaoMamografiaDiagnosticaSchema(RequisicaoMamografiaSchema):
    achados_exame_clinico: Annotated[
        bool,
        Field(
            description="Achados no exame clínico: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="ACHADOS NO EXAME CLÍNICO",
        ),
    ] = False
    exame_clinico_mama_direita_lesao_papilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Exame clínico da mama direita: Lesão papilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA DIREITA - LESÃO PAPILAR",
        ),
    ]
    exame_clinico_mama_direita_descarga_papilar_espontanea: Annotated[
        Optional[TipoDescargaPapilar],
        Field(
            description="Exame clínico da mama direita: Tipo de descarga papilar (01=Cristalina, 02=Hemorrágica)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA DIREITA - DESCARGA PAPILAR ESPONTÂNEA",
        ),
    ] = None
    exame_clinico_mama_direita_nodulo_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama direita: Localização do nódulo (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA DIREITA - NÓDULO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_direita_espessamento_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama direita: Localização do espessamento (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA DIREITA - ESPESSAMENTO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_direita_linfonodo_palpavel: Annotated[
        Optional[List[LocalizacaoLinfonodo]],
        Field(
            description="Exame clínico da mama direita: Linfonodo palpável (01=Axilar, 02=Supraclavicular)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA DIREITA - LINFONODO PALPÁVEL",
        ),
    ] = None
    exame_clinico_mama_esquerda_lesao_papilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Exame clínico da mama esquerda: Lesão papilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA ESQUERDA - LESÃO PAPILAR",
        ),
    ] = None
    exame_clinico_mama_esquerda_descarga_papilar_espontanea: Annotated[
        Optional[TipoDescargaPapilar],
        Field(
            description="Exame clínico da mama esquerda: Tipo de descarga papilar (01=Cristalina, 02=Hemorrágica)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA ESQUERDA - DESCARGA PAPILAR ESPONTÂNEA",
        ),
    ] = None
    exame_clinico_mama_esquerda_nodulo_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama esquerda: Localização do nódulo (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA ESQUERDA - NÓDULO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_esquerda_espessamento_localizacao: Annotated[
        Optional[List[LocalizacaoMama]],
        Field(
            description="Exame clínico da mama esquerda: Localização do espessamento (01=QSL, 02=QIL, 03=QSM, 04=QIM, 05=UQLat, 06=UQsup, 07=UQmed, 08=UQinf, 09=RRA, 10=PA)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA ESQUERDA - ESPESSAMENTO LOCALIZAÇÃO",
        ),
    ] = None
    exame_clinico_mama_esquerda_linfonodo_palpavel: Annotated[
        Optional[List[LocalizacaoLinfonodo]],
        Field(
            description="Exame clínico da mama esquerda: Linfonodo palpável (01=Axilar, 02=Supraclavicular)",
            json_schema_extra={"x-widget": "checkbox"},
            title="MAMA ESQUERDA - LINFONODO PALPÁVEL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3: Annotated[
        bool,
        Field(
            description="Controle radiológico de lesão categoria 3: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3",
        ),
    ] = False
    controle_radiologico_lesao_categoria_3_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - NÓDULO",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama direita: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    # continue com a mama esquerda
    controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_radiologico_lesao_categoria_3_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle radiológico de lesão categoria 3 na mama esquerda: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE RADIOLOGICO DE LESÃO CATEGORIA 3 > MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None
    lesao_diagnostico_cancer: Annotated[
        bool,
        Field(
            description="Lesão diagnóstico de câncer: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER",
        ),
    ] = False
    lesao_diagnostico_cancer_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - NÓDULO",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama direita: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    lesao_diagnostico_cancer_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Lesão diagnóstico de câncer na mama esquerda: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="LESÃO COM DIAGNÓSTICO DE CÂNCER > MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None
    avaliacao_resposta_quimioterapia_neoadjuvante: Annotated[
        bool,
        Field(
            description="Avaliação da resposta à quimioterapia neoadjuvante: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="AVALIAÇÃO DA RESPOSTA À QUIMIOTERAPIA NEADJUVANTE",
        ),
    ] = False
    avaliacao_resposta_quimioterapia_lateralidade: Annotated[
        Optional[Lateralidade],
        Field(
            description="Avaliação da resposta à quimioterapia: Lateralidade (02=Direita, 01=Esquerda, 03=Ambas)",
            json_schema_extra={"x-widget": "radio"},
            title="AVALIAÇÃO DA RESPOSTA À QUIMIOTERAPIA NEOADJUVANTE - LATERALIDADE",
        ),
    ] = None
    revisao_mamografia_outra_instituicao: Annotated[
        bool,
        Field(
            description="Revisão de mamografia em outra instituição: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO",
        ),
    ] = False
    revisao_mamografia_outra_instituicao_mama_direita_categoria_0: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 0 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 0",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_3: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 3 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 3",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_4: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 4 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 4",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_direita_categoria_5: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama direita: Categoria 5 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA DIREITA - CATEGORIA 5",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 0 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 0",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 3 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 3",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 4 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 4",
        ),
    ] = None
    revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5: Annotated[
        Optional[YesOrNone],
        Field(
            description="Revisão de mamografia em outra instituição na mama esquerda: Categoria 5 (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="REVISÃO DE MAMOGRAFIA REALIZADA EM OUTRA INSTITUIÇÃO > MAMA ESQUERDA - CATEGORIA 5",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna: Annotated[
        bool,
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna: True=Sim, False=Não",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA",
        ),
    ] = False
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - NÓDULO",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - ÁREA DENSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_direita_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama direita: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA DIREITA - LINFONODO AXILAR",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_nodulo: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Nódulo (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - NÓDULO",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_microcalcificacoes: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Microcalcificações (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - MICROCALCIFICAÇÕES",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Assimetria focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - ASSIMETRIA FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_assimetria_difusa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Assimetria difusa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - ASSIMETRIA DIFUSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_area_densa: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Área densa (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - ÁREA DENSA",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_distorcao_focal: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Distorção focal (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - DISTORÇÃO FOCAL",
        ),
    ] = None
    controle_lesao_pos_biopsia_paaf_benigna_mama_esquerda_linfonodo_axilar: Annotated[
        Optional[YesOrNone],
        Field(
            description="Controle de lesão pós-biópsia PAAF benigna na mama esquerda: Linfonodo axilar (S=Sim, None=Não)",
            json_schema_extra={"x-widget": "checkbox"},
            title="CONTROLE DE LESÃO PÓS-BIÓPSIA PAAF BENIGNA > MAMA ESQUERDA - LINFONODO AXILAR",
        ),
    ] = None

    @model_validator(mode="after")
    def valida_grupos(cls, values):
        # grupo achados_exame_clinico
        fields_achados = [
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
        if any(getattr(values, f) is not None for f in fields_achados):
            values.achados_exame_clinico = True

        # grupo controle_radiologico_lesao_categoria_3
        fields_controle_radiologico = [
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
        if any(getattr(values, f) is not None for f in fields_controle_radiologico):
            values.controle_radiologico_lesao_categoria_3 = True

        # grupo lesao_diagnostico_cancer
        fields_lesao_cancer = [
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
        if any(getattr(values, f) is not None for f in fields_lesao_cancer):
            values.lesao_diagnostico_cancer = True

        # grupo avaliacao_resposta_quimioterapia_neoadjuvante
        if values.avaliacao_resposta_quimioterapia_lateralidade is not None:
            values.avaliacao_resposta_quimioterapia_neoadjuvante = True

        # grupo revisao_mamografia_outra_instituicao
        fields_revisao = [
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_0",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_3",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_4",
            "revisao_mamografia_outra_instituicao_mama_direita_categoria_5",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_0",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_3",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_4",
            "revisao_mamografia_outra_instituicao_mama_esquerda_categoria_5",
        ]
        if any(getattr(values, f) is not None for f in fields_revisao):
            values.revisao_mamografia_outra_instituicao = True

        # grupo controle_lesao_pos_biopsia_paaf_benigna
        fields_controle_paaf = [
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
        if any(getattr(values, f) is not None for f in fields_controle_paaf):
            values.controle_lesao_pos_biopsia_paaf_benigna = True

        return values
