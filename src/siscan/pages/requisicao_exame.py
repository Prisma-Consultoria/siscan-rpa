import logging

from src.siscan.pages.webpage import SiscanWebPage
from src.siscan.pages.utils.xpath_constructor import XPathConstructor

from src.siscan.pages.exception import CartaoSusNotFoundError, SiscanException

logger = logging.getLogger(__name__)


class RequisicaoExame(SiscanWebPage):
    # Mapeamento entre as chaves do dicionário e o label do formulário
    MAP_DATA_LABEL = {
        "apelido": ("Apelido", "text"),
        "escolaridade": ("Escolaridade:", "select"),
        "ponto_de_referencia": ("Ponto de Referência", "text"),
        "tipo_exame_colo": ("Colo", "radio"),
        "tipo_exame_mama": ("Mama", "radio"),
        "unidade_requisitante": ("Unidade Requisitante", "select"),
    }

    def get_map_label(self) -> dict[str, tuple[str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos labels e tipos.

        Retorna
        -------
        dict[str, tuple[str, str]]
            Dicionário onde a chave é o nome do campo e o valor é uma tupla
            contendo o label e o tipo do campo.
        """
        return {
            "cartao_sus": ("Cartão SUS", "input"),
            # "tipo_exame": ("Tipo de Exame", "select"),
            # "prestador": ("Prestador", "select"),
            # "unidade_requisitante": ("Unidade Requisitante", "select"),
            **self.MAP_DATA_LABEL,
        }

    def access_manage_exam(self):
        self.access_menu("EXAME", "GERENCIAR EXAME")

    def _new_exam(self, event_button: bool = False) -> XPathConstructor:
        self.access_manage_exam()

        if event_button:

            xpath = XPathConstructor(self.context)
            xpath.find_form_anchor_button("Novo Exame").click()

        xpath.wait_page_ready()
        return xpath

    def find_cartao_sus(self, data: dict):
        self._find_cartao_sus(data, menu_action=self._new_exam)

    def insert(self, data: dict):
        """
        Preenche o formulário de novo exame de acordo com os campos informados.

        Parâmetros
        ----------
        campos : dict
            Dicionário onde a chave é o nome amigável do campo (ex: "Cartão SUS")
            e o valor é o dado a ser inserido.
        """
        xpath = self._new_exam(event_button=True)

        # 1o passo: Preenche o campo Cartão SUS e chama o
        # evento onblur do campo
        self.fill_cartao_sus(self._get_value("cartao_sus", data))

        # 2o passo: Define o tipo de exame para então poder habilitar
        # os campos de Prestador e Unidade Requisitante
        type_exam_elem = xpath.find_form_input(
            self._get_label("tipo_exame_mama"),
            self._get_label_type("tipo_exame_mama")
        )
        type_exam_elem.fill(self._get_value("tipo_exame_mama", data),
                            self._get_label_type("tipo_exame_mama"))

        # 3o passo: Obtem os valores do campo select Unidade Requisitante
        # e atualiza o mapeamento de campos
        xpath.find_form_input(self._get_label("unidade_requisitante"),
                              self._get_label_type("unidade_requisitante"))
        self.update_field_map_from_select("unidade_requisitante", xpath)

        # 4o passo: Preenche os campos adicionais do formulário
        fields_map, data_final = self.mount_fields_map_and_data(
            data,
            self.MAP_DATA_LABEL,
            suffix="",
        )
        xpath.fill_form_fields(data_final, fields_map)

        print("9999999", self.FIELDS_MAP['unidade_requisitante'].keys())

        # xpath.find_form_button("Avançar").click()


    def _fill_select_field(self, xpath: XPathConstructor, label: str, valor: str):
        """
        Preenche um campo do tipo <select> (dropdown) associado ao label informado.

        Parâmetros
        ----------
        xpath : XPathConstructor
            Instância do XPathConstructor.
        label : str
            Label associado ao campo.
        valor : str
            Valor a ser selecionado (texto da opção).
        """
        # Localiza o select após o label
        xpath._xpath = f"//label[contains(normalize-space(.), '{label}')]/following-sibling::select[1]"
        logger.debug(f"Localizando select '{label}' para selecionar valor '{valor}'")
        locator = xpath.wait_and_get()
        locator.select_option(label=valor)
        xpath.reset()

#         O campo Cartão SUS deve ser informado.
# O campo Tipo de Exame deve ser informado.
# O campo Prestador deve ser informado.
# O campo Unidade Requisitante deve ser informado.
