from typing import Union

from pathlib import Path

import logging

from src.siscan.exception import CartaoSusNotFoundError, \
    SiscanInvalidFieldValueError
from src.siscan.requisicao_exame import RequisicaoExame
from src.siscan.utils.SchemaMapExtractor import SchemaMapExtractor
from src.siscan.webtools.webpage import RequirementLevel
from src.siscan.webtools.xpath_constructor import XPathConstructor, InputType

logger = logging.getLogger(__name__)


class RequisicaoExameMamografia(RequisicaoExame):
    # manual https://www.inca.gov.br/sites/ufu.sti.inca.local/files/media/document/manual_siscan_modulo2_2021_1.pdf
    # Campos específicos deste formulário
    MAP_SCHEMA_FIELDS = [
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
        "mamografia_de_rastreamento"
    ]

    FIELDS_MAP = {
        "tipo_exame_mama": {
            "01": "Mamografia",
            "03": "Cito de Mama",
            "05": "Histo de Mama",
        }
    }
    def __init__(self, url_base: str, user: str, password: str):
        schema_path = Path(
            __file__).parent / "schemas" / "requisicao_exame_mamografia_rastreamento.schema.json"

        super().__init__(url_base, user, password, schema_path)

        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            schema_path, fields=RequisicaoExameMamografia.MAP_SCHEMA_FIELDS)
        RequisicaoExameMamografia.MAP_DATA_LABEL = map_data_label
        self.FIELDS_MAP.update(fields_map)

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia
        data["tipo_exame_mama"] = "01"  # 01-Mamografia
        # Define o tipo de mamografia como "Rastreamento"
        data["tipo_de_mamografia"] = "02"  # 02-Rastreamento

        super().validation(data)

    def get_map_label(self) -> dict[str, tuple[str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos
        labels e tipos, específico para o exame de Mamografia.

        Retorna
        -------
        dict[str, tuple[str, str]]
            Dicionário onde a chave é o nome do campo e o valor é uma tupla
            contendo o label e o tipo do campo.
        """
        map_label = {
            **RequisicaoExameMamografia.MAP_DATA_LABEL,
        }
        map_label.update(super().get_map_label())
        return map_label

    def selecionar_tipo_exame(self, data: dict):
        """
        Seleciona o tipo de exame como Mamografia.
        """
        self.select_value("tipo_exame_mama", data)

    def preecher_tem_nodulo_ou_caroco_na_mama(self, data: dict):
        """
        Preenche o campo de nódulo ou caroço na mama com base nos dados
        fornecidos.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário.
        """
        nome_campo = "tem_nodulo_ou_caroco_na_mama"
        option_values = self.get_field_value(nome_campo, data)
        self.select_value(nome_campo, {nome_campo: option_values})

    def preecher_fez_mamografia_alguma_vez(self, data: dict):
        # Para "FEZ MAMOGRAFIA ALGUMA VEZ?"
        self.preencher_campo_condicional(
            data,
            campo_chave='fez_mamografia_alguma_vez',
            valor_verdadeiro='Sim',
            campos_dependentes=['ano_que_fez_a_ultima_mamografia'],
            label_dependente='Ano:',
            erro_dependente_msg='O campo ano_que_fez_a_ultima_mamografia não '
                                'deve ser preenchido quando a paciente não '
                                'realizou mamografia.'
        )

    def preenche_fez_radioterapia_na_mama_ou_no_plastao(self, data: dict):
        # Para "FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?"
        breakpoint()
        text, value = self.select_value(
            "fez_radioterapia_na_mama_ou_no_plastrao", data)
        if text == "Sim":
            # Para "RADIOTERAPIA - LOCALIZAÇÃO"
            self.preencher_campo_dependente_multiplo(
                data,
                campo_chave='radioterapia_localizacao',
                condicoes_dependentes={
                    "01": ["ano_da_radioterapia_esquerda"],
                    "02": ["ano_da_radioterapia_direita"],
                    "03": ["ano_da_radioterapia_direita",
                           "ano_da_radioterapia_esquerda"],
                },
                label_dependentes={
                    "ano_da_radioterapia_direita": "Ano:",
                    "ano_da_radioterapia_esquerda": "Ano:",
                },
                erro_dependente_msg="Campos de ano da radioterapia "
                                    "obrigatórios conforme a localização."
            )


    def preencher(self, data: dict):
        """
        Preenche o formulário de requisição de exame com os dados fornecidos.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário.
        """
        self.validation(data)

        # Verifica se o Cartão SUS foi informado
        if not data.get("cartao_sus"):
            raise CartaoSusNotFoundError(self.context,
                                         "Cartão SUS não informado.")

        super().preencher(data)

        xpath = XPathConstructor(self.context)
        xpath.find_form_button("Avançar").click()

        self.preecher_fez_mamografia_alguma_vez(data)
        self.preenche_fez_radioterapia_na_mama_ou_no_plastao(data)

        fields_map, data_final = self.mount_fields_map_and_data(
            data,
            RequisicaoExameMamografia.MAP_DATA_LABEL,
            suffix="",
        )

        # Remove os campos que já foram preenchidos
        # fields_map.pop('tem_nodulo_ou_caroco_na_mama')


        breakpoint()
        xpath.fill_form_fields(data_final, fields_map)


    def get_input_xpath_cirurgia(
            self, nome_campo: str, lado: str) -> XPathConstructor:
        """
        Retorna o XPathConstructor para o campo de input do procedimento
        informado, para o lado especificado ('direito' ou 'esquerdo').

        Parâmetros
        ----------
        nome_campo : str
            Nome do procedimento (exato conforme tela).
        lado : str
            'direito' ou 'esquerdo'

        Retorno
        -------
        XPathConstructor:
            XPath correspondente ao campo <input> desejado.

        Exemplo
        -------
        >>> get_input_xpath_cirurgia("Biópsia cirúrgica incisional", "direito")
        "//input[@id='frm:anoBiopsiaCirurgicaIncisionalDireita']"
        """
        PROCEDIMENTO_MAP = {
            "Biópsia cirúrgica incisional": "BiopsiaCirurgicaIncisional",
            "Biópsia cirúrgica excisional": "BiopsiaCirurgicaExcisional",
            "Segmentectomia": "Segmentectomia",
            "Centralectomia": "Centralectomia",
            "Dutectomia": "Dutectomia",
            "Mastectomia": "Mastectomia",
            "Mastectomia poupadora de pele": "MastectomiaPoupadoraPele",
            "Mastectomia poupadora de pele e complexo aréolo papilar":
                "MastectomiaPoupadoraPeleComplexoPapilar",
            "Linfadenectomia axilar": "LinfadenectomiaAxilar",
            "Biópsia de linfonodo sentinela": "BiopsiaLinfonodoSentinela",
            "Reconstrução mamária": "ReconstrucaoMamaria",
            "Mastoplastia redutora": "MastoplastiaRedutora",
            "Inclusão de implantes": "InclusaoImplantes",
        }
        lado = lado.lower()
        if lado not in ("direito", "esquerdo"):
            raise ValueError("O lado deve ser 'direito' ou 'esquerdo'.")
        if nome_campo not in PROCEDIMENTO_MAP:
            raise ValueError(f"Procedimento '{nome_campo}' não reconhecido.")

        frag = PROCEDIMENTO_MAP[nome_campo]
        lado_cap = "Direita" if lado == "direito" else "Esquerda"
        input_id = f"frm:ano{frag}{lado_cap}"
        xpath = f"//input[@id='{input_id}']"
        return XPathConstructor(self.context, xpath=xpath)

