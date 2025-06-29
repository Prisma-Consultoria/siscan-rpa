import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.siscan.schema.RequisicaoMamografiaRastreamentoSchema import (
    RequisicaoMamografiaRastreamentoSchema,
    TemNoduloOuCarocoNaMama,
    YNIDK,
    FezRadioterapiaNaMamaOuNoPlastrao,
    RadioterapiaLocalizacao,
    TipoDeMamografia,
    MamografiaDeRastreamento,
)


def _load_data(json_path: Path) -> dict:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    # garantir campos necessários para validações
    data.setdefault("tipo_de_mamografia", TipoDeMamografia.RASTREAMENTO.value)
    # caso mamografia de rastreamento seja exigida
    data.setdefault("mamografia_de_rastreamento", MamografiaDeRastreamento.field_01.value)
    # definir valor neutro para radioterapia e remover campos dependentes,
    # permitindo que cada teste configure os valores necessários
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = (
        FezRadioterapiaNaMamaOuNoPlastrao.field_02.value
    )
    data.pop("radioterapia_localizacao", None)
    data.pop("ano_da_radioterapia_direita", None)
    data.pop("ano_da_radioterapia_esquerda", None)
    return data


@pytest.fixture
def base_data(fake_json_file):
    return _load_data(Path(fake_json_file))


# 1) Teste de tem_nodulo_ou_caroco_na_mama
@pytest.mark.parametrize("valores", [["04"], ["01", "02"]])
def test_tem_nodulo_validos(base_data, valores):
    data = base_data.copy()
    data["tem_nodulo_ou_caroco_na_mama"] = valores
    # ['04'] ou ['01','02'] são válidos
    model = RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    assert isinstance(model, RequisicaoMamografiaRastreamentoSchema)


@pytest.mark.parametrize("valores", [["04", "01"], ["04", "02"]])
def test_tem_nodulo_combinacoes_invalidas(base_data, valores):
    data = base_data.copy()
    data["tem_nodulo_ou_caroco_na_mama"] = valores
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


# 2) Teste de fez_mamografia_alguma_vez e ano_que_fez_a_ultima_mamografia

def test_fez_mamografia_sem_ano(base_data):
    data = base_data.copy()
    data["fez_mamografia_alguma_vez"] = YNIDK.SIM.value
    data.pop("ano_que_fez_a_ultima_mamografia", None)
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_nao_fez_mamografia_com_ano(base_data):
    data = base_data.copy()
    data["fez_mamografia_alguma_vez"] = YNIDK.NAO.value
    data["ano_que_fez_a_ultima_mamografia"] = "2025"
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_mamografia_valida_com_ano(base_data):
    data = base_data.copy()
    data["fez_mamografia_alguma_vez"] = YNIDK.SIM.value
    data["ano_que_fez_a_ultima_mamografia"] = "2025"
    model = RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    assert model.ano_que_fez_a_ultima_mamografia == "2025"


# 3) Teste de fez_radioterapia e radioterapia_localizacao

def test_fez_radioterapia_sem_localizacao(base_data):
    data = base_data.copy()
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = FezRadioterapiaNaMamaOuNoPlastrao.field_01.value
    data.pop("radioterapia_localizacao", None)
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_nao_fez_radioterapia_com_localizacao(base_data):
    data = base_data.copy()
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = FezRadioterapiaNaMamaOuNoPlastrao.field_02.value
    data["radioterapia_localizacao"] = RadioterapiaLocalizacao.field_01.value
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_radioterapia_valida_com_localizacao(base_data):
    data = base_data.copy()
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = FezRadioterapiaNaMamaOuNoPlastrao.field_01.value
    data["radioterapia_localizacao"] = RadioterapiaLocalizacao.field_02.value
    data["ano_da_radioterapia_direita"] = "2023"
    model = RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    assert model.ano_da_radioterapia_direita == "2023"

# 4) Teste de dependências de radioterapia_localizacao
@pytest.mark.parametrize("loc, campo", [
    (RadioterapiaLocalizacao.field_02, "ano_da_radioterapia_direita"),
    (RadioterapiaLocalizacao.field_01, "ano_da_radioterapia_esquerda"),
])
def test_radioterapia_localizacao_dependencia(base_data, loc, campo):
    data = base_data.copy()
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = FezRadioterapiaNaMamaOuNoPlastrao.field_01.value
    data["radioterapia_localizacao"] = loc.value
    # campo obrigatório ausente
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_radioterapia_ambas_direita_esquerda(base_data):
    data = base_data.copy()
    data["fez_radioterapia_na_mama_ou_no_plastrao"] = FezRadioterapiaNaMamaOuNoPlastrao.field_01.value
    data["radioterapia_localizacao"] = RadioterapiaLocalizacao.field_03.value
    # falta ambos
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    # agora com ambos
    data["ano_da_radioterapia_direita"] = "2023"
    data["ano_da_radioterapia_esquerda"] = "2024"
    model = RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    assert model.ano_da_radioterapia_direita == "2023" and model.ano_da_radioterapia_esquerda == "2024"

# 5) Teste de tipo_de_mamografia

def test_tipo_mamografia_rastreamento_sem_mamo(base_data):
    data = base_data.copy()
    data["tipo_de_mamografia"] = TipoDeMamografia.RASTREAMENTO.value
    data.pop("mamografia_de_rastreamento", None)
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_tipo_mamografia_diagnostica_com_mamo(base_data):
    data = base_data.copy()
    data["tipo_de_mamografia"] = TipoDeMamografia.DIAGNOSTICA.value
    data["mamografia_de_rastreamento"] = MamografiaDeRastreamento.field_02.value
    with pytest.raises(ValidationError):
        RequisicaoMamografiaRastreamentoSchema.model_validate(data)


def test_tipo_mamografia_diagnostica_sem_mamo(base_data):
    data = base_data.copy()
    data["tipo_de_mamografia"] = TipoDeMamografia.DIAGNOSTICA.value
    data.pop("mamografia_de_rastreamento", None)
    model = RequisicaoMamografiaRastreamentoSchema.model_validate(data)
    assert model.tipo_de_mamografia == TipoDeMamografia.DIAGNOSTICA
