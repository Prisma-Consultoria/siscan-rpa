#
# Define a classe base RequisicaoExame, que representa a lógica de automação
# para o preenchimento da requisição genérica de exames.
#
# Centraliza fluxos como autenticação, seleção de unidade requisitante,
# prestador, preenchimento dos campos gerais do exame e validação dos dados.
#
# Serve de base para os demais tipos de requisição de exame por herança
#
import logging
from abc import abstractmethod

from src.siscan.exception import SiscanInvalidFieldValueError
from src.siscan.schema.requisicao_novo_exame_schema import \
    RequisicaoNovoExameSchema
from src.siscan.webpage.base import SiscanWebPage, \
    ensure_metadata_schema_fields
from src.siscan.webpage.xpath_constructor import (XPathConstructor as XPE)

logger = logging.getLogger(__name__)


class RequisicaoExame(SiscanWebPage):
    _schema_model = RequisicaoNovoExameSchema

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url, user, password)
        ensure_metadata_schema_fields(RequisicaoExame)


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


    async def buscar_cartao_sus(self, data: dict):
        await self._buscar_cartao_sus(data, menu_action=self._novo_exame)

    async def _acessar_menu_gerenciar_exame(self):
        await self.acessar_menu("EXAME", "GERENCIAR EXAME")

    async def _novo_exame(self, event_button: bool = False) -> XPE:
        # TOFIX Não deveria ter um comando genérico para botões em vez de algo específico?
        await self._acessar_menu_gerenciar_exame()

        xpath = await XPE.create(self.context)
        if event_button:
            # ``find_form_anchor_button`` é síncrono e apenas configura o XPath
            # interno. O clique propriamente dito é assíncrono, portanto
            # chamamos ``handle_click`` e aguardamos sua conclusão.
            await xpath.find_form_anchor_button("Novo Exame").handle_click()

        await self.wait_page_ready()
        return xpath

    async def _seleciona_unidade_requisitante(self, data: dict | None = None):
        """
        Seleciona e valida a unidade requisitante a partir dos dados fornecidos.
        """
        nome_campo = "cnes_unidade_requisitante"
        await self.load_select_options(nome_campo)

        # Atualiza o mapeamento de campos usando apenas o código CNES antes do hífen.
        for k, v in list(self.FIELDS_VALUE_MAP[nome_campo].items()):
            key = f"{k.split('-')[0].strip()}"
            self.FIELDS_VALUE_MAP[nome_campo][key] = v

            # Remove o item original que contém o hífen
            if v != "0":
                del self.FIELDS_VALUE_MAP[nome_campo][k]

        text, value = await self.select_value(nome_campo, data)
        if value == "0":
            raise SiscanInvalidFieldValueError(
                self.context,
                field_name=nome_campo,
                data=data,
                options_values=self.FIELDS_VALUE_MAP[nome_campo].keys(),
            )
        data.pop(nome_campo, None)

    async def _selecionar_prestador(self, data: dict | None = None):
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
                options_values=self.FIELDS_VALUE_MAP[nome_campo].keys(),
            )
        data.pop(nome_campo, None)

    async def preencher(self, data: dict):
        """
        Preenche o formulário de novo exame de acordo com os campos informados.
        """
        breakpoint()
        self.validation(data)

        await self._authenticate()

        xpath = await self._novo_exame(event_button=True)

        # 1o passo: Preenche o campo Cartão SUS e chama o evento onblur do campo
        await self.preencher_cartao_sus(
            numero=self.get_field_value("cartao_sus", data),
            timeout=20)

        # 2o passo: Define o tipo de exame para então poder habilitar os
        # campos de Prestador e Unidade Requisitante
        await self.selecionar_tipo_exame(data)

        # 3o passo: Obtem os valores do campo select Unidade Requisitante,
        # atualiza o mapeamento de campos e preenche o campo
        await self._seleciona_unidade_requisitante(data)

        # 4o passo: Obtem os valores do campo select Prestador, atualiza o
        # mapeamento de campos e preenche o campo
        await self._selecionar_prestador(data)

        # 5o passo: Preenche os campos adicionais do formulário
        # apelido, escolaridade, ponto_de_referenciea
        await self.fill_form_fields(
            data,
            self.get_fields_mapping(),
            suffix=""
        )
        await self.take_screenshot("screenshot_03_requisicao_exame.png")
