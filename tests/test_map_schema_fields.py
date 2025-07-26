import pytest


def test_requiscao_mamografia_map_schema_fields():
    from src.siscan.classes.requisicao_exame_mamografia import RequisicaoExameMamografia

    assert set(RequisicaoExameMamografia.MAP_SCHEMA_FIELDS) == {
        "num_prontuario",
        "tem_nodulo_ou_caroco_na_mama",
        "apresenta_risco_elevado_para_cancer_mama",
        "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional",
        "fez_mamografia_alguma_vez",
        "ano_que_fez_a_ultima_mamografia",
        "fez_radioterapia_na_mama_ou_no_plastrao",
        "radioterapia_localizacao",
        "ano_da_radioterapia_direita",
        "ano_da_radioterapia_esquerda",
        "fez_cirurgia_de_mama",
        "ano_biopsia_cirurgica_incisional_direita",
        "ano_biopsia_cirurgica_incisional_esquerda",
        "ano_biopsia_cirurgica_excisional_direita",
        "ano_biopsia_cirurgica_excisional_esquerda",
        "ano_segmentectomia_direita",
        "ano_segmentectomia_esquerda",
        "ano_centralectomia_direita",
        "ano_centralectomia_esquerda",
        "ano_dutectomia_direita",
        "ano_dutectomia_esquerda",
        "ano_mastectomia_direita",
        "ano_mastectomia_esquerda",
        "ano_mastectomia_poupadora_pele_direita",
        "ano_mastectomia_poupadora_pele_esquerda",
        "ano_mastectomia_poupadora_pele_complexo_papilar_direita",
        "ano_mastectomia_poupadora_pele_complexo_papilar_esquerda",
        "ano_linfadenectomia_axilar_direita",
        "ano_linfadenectomia_axilar_esquerda",
        "ano_biopsia_linfonodo_sentinela_direita",
        "ano_biopsia_linfonodo_sentinela_esquerda",
        "ano_reconstrucao_mamaria_direita",
        "ano_reconstrucao_mamaria_esquerda",
        "ano_mastoplastia_redutora_direita",
        "ano_mastoplastia_redutora_esquerda",
        "ano_inclusao_implantes_direita",
        "ano_inclusao_implantes_esquerda",
        "tipo_de_mamografia",
        "data_da_solicitacao",
        "cns_responsavel_coleta"
    }

def test_requiscao_mamografia_rastreamento_map_schema_fields():
    from src.siscan.classes.requisicao_exame_mamografia_rastreio import RequisicaoExameMamografiaRastreio

    assert set(RequisicaoExameMamografiaRastreio.MAP_SCHEMA_FIELDS) == {
        "tipo_mamografia_de_rastreamento",
    }
