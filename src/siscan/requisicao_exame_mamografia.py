import logging

from src.siscan.exception import CartaoSusNotFoundError, \
    SiscanInvalidFieldValueError
from src.siscan.requisicao_exame import RequisicaoExame
from src.siscan.webtools.webpage import RequirementLevel
from src.siscan.webtools.xpath_constructor import XPathConstructor, InputType

logger = logging.getLogger(__name__)


class RequisicaoExameMamografia(RequisicaoExame):
    # Mapeamento entre as chaves do dicionário e o label do formulário
    # manual https://www.inca.gov.br/sites/ufu.sti.inca.local/files/media/document/manual_siscan_modulo2_2021_1.pdf
    MAP_DATA_LABEL = {
        "num_prontuario": ("Nº do Prontuário",
                           InputType.TEXT, RequirementLevel.REQUIRED),
        "tem_nodulo_ou_caroco_na_mama": (
            "TEM NÓDULO OU CAROÇO NA MAMA?", InputType.CHECKBOX,
            RequirementLevel.REQUIRED),
        "apresenta_risco_elevado_para_cancer_mama": (
            "APRESENTA RISCO ELEVADO PARA CÂNCER DE MAMA?", InputType.RADIO,
            RequirementLevel.REQUIRED),
        "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional": (
            "ANTES DESTA CONSULTA, TEVE AS MAMAS EXAMINADAS POR UM PROFISSIONAL DE SAÚDE?",
            InputType.RADIO, RequirementLevel.REQUIRED),

        "fez_mamografia_alguma_vez": (
            "FEZ MAMOGRAFIA ALGUMA VEZ?", InputType.RADIO,
            RequirementLevel.REQUIRED),
        # Se sim, habilita o campo (obrigatório)
        # "ANO QUE FEZ A ÚLTIMA MAMOGRAFIA"/"Ano: "
        "ano_que_fez_a_ultima_mamografia": ("QUANDO FEZ A ÚLTIMA MAMOGRAFIA?",
                                            InputType.TEXT,
                                            RequirementLevel.REQUIRED),

        "fez_radioterapia_na_mama_ou_no_plastrao": (
            "FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?", InputType.RADIO,
            RequirementLevel.REQUIRED),
        # Se sim, habilita "RADIOTERAPIA - LOCALIZAÇÃO"
        "radioterapia_localizacao": ("RADIOTERAPIA - LOCALIZAÇÃO",
                                     InputType.RADIO,
                                     RequirementLevel.OPTIONAL),
        # Se "Ambas", habilita os campos "Direita" e "Esquerda" (obrigatório)
        # Se "Direita", habilita o campo
        # "ANO DA RADIOTERAPIA - DIREITA"/"Ano da Radioterapia - Direita: "
        "ano_da_radioterapia_direita": ("ANO DA RADIOTERAPIA - DIREITA",
                                        InputType.TEXT,
                                        RequirementLevel.OPTIONAL),
        # Se "Esquerda", habilita o campo
        # "ANO DA RADIOTERAPIA - ESQUERDA"/"Ano da Radioterapia - Esquerda: "
        "ano_da_radioterapia_esquerda": ("ANO DA RADIOTERAPIA - ESQUERDA",
                                         InputType.TEXT,
                                         RequirementLevel.OPTIONAL),

        "fez_cirurgia_de_mama": ("FEZ CIRURGIA DE MAMA?", InputType.RADIO,
                                 RequirementLevel.REQUIRED),
        # Se "Sim", habilita os campos abaixo (opcionais)
        # Procedimentos cirúrgicos de mama – direita/esquerda
        "ano_biopsia_cirurgica_incisional_direita": (
            "Biópsia cirúrgica incisional (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_biopsia_cirurgica_incisional_esquerda": (
            "Biópsia cirúrgica incisional (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_biopsia_cirurgica_excisional_direita": (
            "Biópsia cirúrgica excisional (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_biopsia_cirurgica_excisional_esquerda": (
            "Biópsia cirúrgica excisional (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_segmentectomia_direita": (
            "Segmentectomia (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_segmentectomia_esquerda": (
            "Segmentectomia (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_centralectomia_direita": (
            "Centralectomia (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_centralectomia_esquerda": (
            "Centralectomia (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_dutectomia_direita": (
            "Dutectomia (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_dutectomia_esquerda": (
            "Dutectomia (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastectomia_direita": (
            "Mastectomia (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastectomia_esquerda": (
            "Mastectomia (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastectomia_poupadora_pele_direita": (
            "Mastectomia poupadora de pele (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastectomia_poupadora_pele_esquerda": (
            "Mastectomia poupadora de pele (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastectomia_poupadora_pele_complexo_papilar_direita": (
          "Mastectomia poupadora de pele e complexo aréolo papilar (Direita)",
          InputType.TEXT, RequirementLevel.OPTIONAL),
        "ano_mastectomia_poupadora_pele_complexo_papilar_esquerda": (
          "Mastectomia poupadora de pele e complexo aréolo papilar (Esquerda)",
          InputType.TEXT, RequirementLevel.OPTIONAL),
        "ano_linfadenectomia_axilar_direita": (
            "Linfadenectomia axilar (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_linfadenectomia_axilar_esquerda": (
            "Linfadenectomia axilar (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_biopsia_linfonodo_sentinela_direita": (
            "Biópsia de linfonodo sentinela (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_biopsia_linfonodo_sentinela_esquerda": (
            "Biópsia de linfonodo sentinela (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_reconstrucao_mamaria_direita": (
            "Reconstrução mamária (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_reconstrucao_mamaria_esquerda": (
            "Reconstrução mamária (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastoplastia_redutora_direita": (
            "Mastoplastia redutora (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_mastoplastia_redutora_esquerda": (
            "Mastoplastia redutora (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_inclusao_implantes_direita": (
            "Inclusão de implantes (Direita)", InputType.TEXT,
            RequirementLevel.OPTIONAL),
        "ano_inclusao_implantes_esquerda": (
            "Inclusão de implantes (Esquerda)", InputType.TEXT,
            RequirementLevel.OPTIONAL),

        "tipo_de_mamografia": ("TIPO DE MAMOGRAFIA", InputType.RADIO,
                               RequirementLevel.REQUIRED),
        # Se "Rastreamento", habilita os campos abaixo (obrigatório)
        "mamografia_de_rastreamento": ("MAMOGRAFIA DE RASTREAMENTO",
                                       InputType.RADIO,
                                       RequirementLevel.OPTIONAL)

        # Se "Diagóstica", habilita cos campos abaixo

    }

    FIELDS_MAP = {
        # tipo checkbox, pode marcar mais de uma opção
        # Ao marcar "Não", os anteriores ("01" e "02") são desmarcados
        "tem_nodulo_ou_caroco_na_mama": {
            "01": "01",  # Sim, Mama Direita
            "02": "02",  # Sim, Mama Esquerda
            "04": "04",  # Não
        },
        # tipo radio, só pode marcar uma opção
        "apresenta_risco_elevado_para_cancer_mama": {
            "01": "01",  # Sim
            "02": "02",  # Não
            "03": "03",  # Não Sabe
        },
        "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional": {
            "01": "01",  # Sim
            "02": "02",  # Nunca foram examinadas anteriormente
            "03": "03",  # Não Sabe
        },
        "fez_mamografia_alguma_vez": {
            "01": "01",  # Sim
            "02": "02",  # Não
            "03": "03",  # Não Sabe
        },
        "fez_radioterapia_na_mama_ou_no_plastrao": {
            "01": "01",  # Sim
            "02": "02",  # Não
            "03": "03",  # Não Sabe
        },
        "radioterapia_localizacao": {
            "01": "01",  # Esquerda
            "02": "02",  # Direita
            "03": "03",  # Ambas
        },
        "fez_cirurgia_de_mama": {
            "01": "S",  # Sim
            "02": "N",  # Não
        },
        "tipo_de_mamografia": {
            "01": "01",  # Diagnóstica
            "02": "02",  # Rastreamento
        },
        "mamografia_de_rastreamento": {
            "01": "01",  # População alvo
            "02": "02",  # População de risco elevado (história familiar)
            "03": "03",  # Paciente já tratado de câncer de mama
        }

    }
    FIELDS_MAP.update(RequisicaoExame.FIELDS_MAP)

    def validation(self, data: dict):
        super().validation(data)
        nome_campo = "tem_nodulo_ou_caroco_na_mama"
        if data[nome_campo] == "Não":
            # Se a resposta for "Não", não deve haver opções marcadas
            if any(data.get(key) for key
                   in self.FIELDS_MAP[nome_campo].values()
                   if key != "04"):
                raise SiscanInvalidFieldValueError(
                    context=None,
                    field_name=nome_campo,
                    message=(
                        f"O campo '{self.get_field_label(nome_campo)}' "
                        f"não deve outros itens se existir a opção 'Não'."
                    )
                )

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
        nome_campo = "tipo_exame_mama"

        # Define o tipo de exame como Mamografia
        data[nome_campo] = "Mamografia"
        self.select_value(nome_campo, data)

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
        for option_value in option_values:
            text, value = self.select_value(
                nome_campo, {nome_campo: option_value})

    def preecher_fez_mamografia_alguma_vez(self, data: dict):
        nome_campo = "fez_mamografia_alguma_vez"
        text, value = self.select_value(nome_campo, data)
        ano_ultima_mamografia = data.get("ano_que_fez_a_ultima_mamografia")
        if text == "Sim":
            # Se a resposta for "Sim", preenche o campo adicional
            self.select_field_in_card(
                card_name=self.get_field_label("ano_que_fez_a_ultima_mamografia"),
                field_name="Ano:",
                value=ano_ultima_mamografia
            )
        elif text == "Não" and ano_ultima_mamografia:
            raise SiscanInvalidFieldValueError(
                self.context,
                message=(
                    f"O campo 'Ano' de "
                    f"'{ano_ultima_mamografia}' não deve ser preenchido se a "
                    f"resposta for 'Não' para '{self.get_field_label(nome_campo)}'"
                )
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


        breakpoint()


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

