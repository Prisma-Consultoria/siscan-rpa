from enum import Enum


class YNIDK(Enum):
    SIM = "01"
    NAO = "02"
    NAO_SABE = "03"


class Lateralidade(Enum):
    ESQUERDA = "01"
    DIREITA = "02"
    AMBAS = "03"


class YN(Enum):
    SIM = "01"
    NAO = "02"


class TipoDeMamografia(Enum):
    DIAGNOSTICA = "01"
    RASTREAMENTO = "02"
