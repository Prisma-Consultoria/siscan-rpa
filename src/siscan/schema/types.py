from enum import Enum

class MappedEnum(Enum):
    @classmethod
    def get_external_map(cls) -> dict:
        """
        Retorna o mapeamento externo → interno para a Enum.
        Por padrão, retorna o próprio valor da Enum (identidade).
        """
        return {member.value: member.value for member in cls}


class TipoDeMamografia(MappedEnum):
    DIAGNOSTICA = "01"
    RASTREAMENTO = "02"


class TipoMamografiaRastreamento(MappedEnum):
    POPULACAO_ALVO = "01"
    RISCO_ELEVADO_FAMILIAR = "02"
    CANCER_PREVIO = "03"


class Lateralidade(MappedEnum):
    ESQUERDA = "01"
    DIREITA = "02"
    AMBAS = "03"


class YesNoUnknownCode(MappedEnum):
    SIM = "01"
    NAO = "02"
    NAO_SABE = "03"

    @classmethod
    def get_external_map(cls):
        return {
            "S": cls.SIM.value,
            "N": cls.NAO.value,
            "NS": cls.NAO_SABE.value,
        }


class YesNo(MappedEnum):
    SIM = "S"
    NAO = "N"

class YesNone(MappedEnum):
    SIM = "S"
    NONE = None


class TipoDescargaPapilar(MappedEnum):
    CRISTALINA = "01"
    HEMORRAGICA = "02"
    NONE = "null"


class LocalizacaoMama(MappedEnum):
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

    @classmethod
    def get_external_map(cls):
        return {
            "QSL": cls.QSL.value,
            "QIL": cls.QIL.value,
            "QSM": cls.QSM.value,
            "QIM": cls.QIM.value,
            "UQLAT": cls.UQlat.value,
            "UQSUP": cls.UQsup.value,
            "UQMED": cls.UQmed.value,
            "UQINF": cls.UQinf.value,
            "RRA": cls.RRA.value,
            "PA": cls.PA.value,
        }


class LocalizacaoLinfonodo(MappedEnum):
    AXILAR = "01"
    SUPRACLAVICULAR = "02"


class TemNoduloOuCarocoNaMama(MappedEnum):
    SIM_MAMA_DIREITA = "01"
    SIM_MAMA_ESQUERDA = "02"
    NAO = "04"


