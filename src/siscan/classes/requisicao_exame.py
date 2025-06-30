from typing import Type

from pydantic import BaseModel

from abc import abstractmethod

import logging

from src.siscan.exception import SiscanInvalidFieldValueError
from src.siscan.classes.webpage import SiscanWebPage
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE, InputType
from src.utils.webpage import RequirementLevel

logger = logging.getLogger(__name__)


class RequisicaoExame(SiscanWebPage):
    # Campos específicos deste formulário
    MAP_SCHEMA_FIELDS = [
        "apelido",
        "escolaridade",
        "ponto_de_referencia",
        "tipo_exame_mama",
        "unidade_requisitante",
        "prestador",
    ]

    def __init__(
        self, base_url: str, user: str, password: str, schema_model: Type[BaseModel]
    ):
        super().__init__(base_url, user, password, schema_model)
        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=RequisicaoExame.MAP_SCHEMA_FIELDS
        )
        RequisicaoExame.MAP_DATA_LABEL = map_data_label
        self.FIELDS_MAP.update(fields_map)

    def validation(self, data: dict):
        super().validation(data)

    @abstractmethod
    def selecionar_tipo_exame(self, data: dict):
        """
        Método abstrato para selecionar o tipo de exame.
        Deve ser implementado nas subclasses.
        """
        raise NotImplementedError(
            "O método select_type_exam deve ser implementado na subclasse."
        )

    def get_map_label(self) -> dict[str, tuple[str, str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos labels e tipos.
        """
        map_label = {
            **SiscanWebPage.MAP_DATA_LABEL,
            **RequisicaoExame.MAP_DATA_LABEL,
        }
        map_label["cartao_sus"] = (
            "Cartão SUS",
            InputType.TEXT,
            RequirementLevel.REQUIRED,
        )
        return map_label

    async def acessar_menu_gerenciar_exame(self):
        await self.acessar_menu("EXAME", "GERENCIAR EXAME")

    async def _novo_exame(self, event_button: bool = False) -> XPE:
        # TOFIX Não deveria ter um comando genérico para botões em vez de algo específico?
        await self.acessar_menu_gerenciar_exame()

        xpath = await XPE.create(self.context)
        if event_button:
            # ``find_form_anchor_button`` é síncrono e apenas configura o XPath
            # interno. O clique propriamente dito é assíncrono, portanto
            # chamamos ``handle_click`` e aguardamos sua conclusão.
            await xpath.find_form_anchor_button("Novo Exame").handle_click()

        await xpath.wait_page_ready()
        return xpath

    async def buscar_cartao_sus(self, data: dict):
        await self._buscar_cartao_sus(data, menu_action=self._novo_exame)

    async def seleciona_unidade_requisitante(self, data: dict | None = None):
        """
        Seleciona e valida a unidade requisitante a partir dos dados fornecidos.
        """
        nome_campo = "unidade_requisitante"
        await self.load_select_options(nome_campo)

        # Atualiza o mapeamento de campos usando apenas o código CNES antes do hífen.
        for k, v in list(self.FIELDS_MAP[nome_campo].items()):
            key = f"{k.split('-')[0].strip()}"
            self.FIELDS_MAP[nome_campo][key] = v

            # Remove o item original que contém o hífen
            if v != "0":
                del self.FIELDS_MAP[nome_campo][k]

        text, value = await self.select_value(nome_campo, data)
        if value == "0":
            raise SiscanInvalidFieldValueError(
                self.context,
                field_name=nome_campo,
                data=data,
                options_values=self.FIELDS_MAP[nome_campo].keys(),
            )

    async def selecionar_prestador(self, data: dict | None = None):
        """
        Seleciona e valida o campo 'prestador' a partir dos dados fornecidos.
        """
        nome_campo = "prestador"
        await self.load_select_options(nome_campo)
        text, value = await self.select_value(nome_campo, data)
        if value == "0":
            raise SiscanInvalidFieldValueError(
                self.context,
                field_name=nome_campo,
                data=data,
                options_values=self.FIELDS_MAP[nome_campo].keys(),
            )

    async def preencher(self, data: dict):
        """
        Preenche o formulário de novo exame de acordo com os campos informados.
        """

        self.validation(data)

        xpath = await self._novo_exame(event_button=True)

        # 1o passo: Preenche o campo Cartão SUS e chama o evento onblur do campo
        await self.preencher_cartao_sus(numero=self.get_field_value("cartao_sus", data))

        # 2o passo: Define o tipo de exame para então poder habilitar os campos de Prestador e Unidade Requisitante
        await self.selecionar_tipo_exame(data)

        # 3o passo: Obtem os valores do campo select Unidade Requisitante, atualiza o mapeamento de campos e preenche o campo
        await self.seleciona_unidade_requisitante(data)

        # 4o passo: Obtem os valores do campo select Prestador, atualiza o mapeamento de campos e preenche o campo
        await self.selecionar_prestador(data)

        # 5o passo: Preenche os campos adicionais do formulário Antes, monta o mapeamento de campos e os dados finais
        fields_map, data_final = self.mount_fields_map_and_data(
            data,
            RequisicaoExame.MAP_DATA_LABEL,
            suffix="",
        )

        # Remove os campos que já foram preenchidos
        fields_map.pop("unidade_requisitante")
        fields_map.pop("prestador")

        await xpath.fill_form_fields(data_final, fields_map)
        await self.take_screenshot("screenshot_03_requisicao_exame.png")
