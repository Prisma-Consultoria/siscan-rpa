import logging

from src.siscan.exception import CartaoSusNotFoundError, \
    SiscanUnexpectedFieldFilledError
from src.siscan.requisicao_exame import RequisicaoExame
from src.siscan.webtools.xpath_constructor import XPathConstructor

logger = logging.getLogger(__name__)


class RequisicaoExameMamografia(RequisicaoExame):
    # Mapeamento entre as chaves do dicionário e o label do formulário
    MAP_DATA_LABEL = {
        "num_prontuario": ("Nº do Prontuário", "text"),
        "tem_nodulo_ou_caroco_na_mama": (
            "TEM NÓDULO OU CAROÇO NA MAMA?", "checkbox"),
        "apresenta_risco_elevado_para_cancer_mama": (
            "APRESENTA RISCO ELEVADO PARA CÂNCER DE MAMA?", "radio"),
        "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional": (
            "ANTES DESTA CONSULTA, TEVE AS MAMAS EXAMINADAS POR UM PROFISSIONAL DE SAÚDE?",
            "radio"),

        "fez_mamografia_alguma_vez": ("FEZ MAMOGRAFIA ALGUMA VEZ?", "radio"),
        # Se sim, habilita o campo (obrigatório)
        # "ANO QUE FEZ A ÚLTIMA MAMOGRAFIA"/"Ano: "
        "ano_que_fez_a_ultima_mamografia": ("QUANDO FEZ A ÚLTIMA MAMOGRAFIA?",
                                            "text"),

        "fez_radioterapia_na_mama_ou_no_plastrao": (
            "FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?", "radio"),
        # Se sim, habilita "RADIOTERAPIA - LOCALIZAÇÃO"
        "radioterapia_localizacao": ("RADIOTERAPIA - LOCALIZAÇÃO", "radio"),
        # Se "Ambas", habilita os campos "Direita" e "Esquerda" (obrigatório)
        # Se "Direita", habilita o campo
        # "ANO DA RADIOTERAPIA - DIREITA"/"Ano da Radioterapia - Direita: "
        "ano_da_radioterapia_direita": ("ANO DA RADIOTERAPIA - DIREITA",
                                        "text"),
        # Se "Esquerda", habilita o campo
        # "ANO DA RADIOTERAPIA - ESQUERDA"/"Ano da Radioterapia - Esquerda: "
        "ano_da_radioterapia_esquerda": ("ANO DA RADIOTERAPIA - ESQUERDA",
                                         "text"),

        "fez_cirurgia_de_mama": ("FEZ CIRURGIA DE MAMA?", "radio"),
        # Se "Sim", habilita os campos abaixo (opcionais)

        "tipo_de_mamografia": ("TIPO DE MAMOGRAFIA", "radio"),
        # Se "Rastreamento", habilita os campos abaixo (obrigatório)
        "mamografia_de_rastreamento": ("MAMOGRAFIA DE RASTREAMENTO", "radio")

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
        breakpoint()
        self.FIELDS_MAP[nome_campo]
        if data[nome_campo] == "Não":
            # Se a resposta for "Não", não deve haver opções marcadas
            if any(data.get(key) for key
                   in self.FIELDS_MAP[nome_campo].values()
                   if key != "04"):
                raise SiscanUnexpectedFieldFilledError(
                    self.context,
                    field_name=nome_campo,
                    message=(
                        f"O campo '{self.get_label(nome_campo)}' "
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
        Preenche o campo de nódulo ou caroço na mama com base nos dados fornecidos.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário.
        """
        nome_campo = "tem_nodulo_ou_caroco_na_mama"
        option_values = self.get_value(nome_campo, data)
        for option_value in option_values:
            text, value = self.select_value(
                nome_campo, {nome_campo: option_value})

    def preecher_fez_mamografia_alguma_vez(self, data: dict):
        nome_campo = "fez_mamografia_alguma_vez"
        text, value = self.select_value(nome_campo, data)
        ano_ultima_mamografia = data.get("ano_que_fez_a_ultima_mamografia", "")
        if text == "Sim":
            # Se a resposta for "Sim", preenche o campo adicional
            label = self.get_label("ano_que_fez_a_ultima_mamografia")
            xpath_obj = XPathConstructor(
                self.context,
                xpath=f"//fieldset[legend[normalize-space(text())='{label}']]"
                      f"//label[normalize-space(text())='Ano:']"
                      f"/following-sibling::input[1]")
            xpath_obj.fill(ano_ultima_mamografia)
        elif text == "Não" and ano_ultima_mamografia:
            raise SiscanUnexpectedFieldFilledError(
                self.context,
                message=(
                    f"O campo 'Ano' de "
                    f"'{self.get_label('ano_que_fez_a_ultima_mamografia')}' "
                    f"não deve ser preenchido se a resposta for 'Não' para "
                    f"'{self.get_label(nome_campo)}'"
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
