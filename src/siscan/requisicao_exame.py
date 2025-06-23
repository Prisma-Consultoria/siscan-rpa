from pathlib import Path

from typing import Union

from abc import abstractmethod

import logging

from src.siscan.exception import SiscanInvalidFieldValueError
from src.siscan.siscan_webpage import SiscanWebPage
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor, InputType
from src.utils.webpage import RequirementLevel

logger = logging.getLogger(__name__)


class RequisicaoExame(SiscanWebPage):
    # Campos específicos deste formulário
    MAP_SCHEMA_FIELDS = [
        "apelido",
        "escolaridade",
        "ponto_de_referencia",
        # "tipo_exame_colo",
        "tipo_exame_mama",
        "unidade_requisitante",
        "prestador"
    ]

    def __init__(self, url_base: str, user: str, password: str,
                 schema_path: Union[str, Path]):
        super().__init__(url_base, user, password, schema_path)
        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            schema_path, fields=RequisicaoExame.MAP_SCHEMA_FIELDS)
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
        raise NotImplementedError("O método select_type_exam deve ser "
                                  "implementado na subclasse.")

    def get_map_label(self) -> dict[str, tuple[str, str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos
        labels e tipos.

        Retorna
        -------
        dict[str, tuple[str, str, str]]
            Dicionário onde a chave é o nome do campo e o valor é uma tupla
            contendo o label, o tipo do campo e o nível de
            obrigatoriedade.
        """
        return {
            "cartao_sus": (
                "Cartão SUS",
                InputType.TEXT,
                RequirementLevel.REQUIRED,
            ),
            **RequisicaoExame.MAP_DATA_LABEL,
        }

    async def acesar_menu_gerenciar_exame(self):
        await self.acessar_menu("EXAME", "GERENCIAR EXAME")

    async def _novo_exame(self, event_button: bool = False) -> XPathConstructor:
        await self.acesar_menu_gerenciar_exame()

        if event_button:

            xpath = XPathConstructor(self.context)
            await (await xpath.find_form_anchor_button("Novo Exame")).handle_click()

        await xpath.wait_page_ready()
        return xpath

    async def buscar_cartao_sus(self, data: dict):
        await self._buscar_cartao_sus(data, menu_action=self._novo_exame)

    def seleciona_unidade_requisitante(self, data: dict | None = None):
        """
        Seleciona e valida a unidade requisitante a partir dos dados
        fornecidos.

        Este método realiza o carregamento e o mapeamento das opções
        disponíveis para o campo 'unidade_requisitante' (campo responsável
        pelo código CNES da unidade requisitante).
        Inicialmente, carrega as opções do campo select, atualizando o
        mapeamento (`FIELDS_MAP`) para considerar apenas o código CNES (parte
        antes do hífen). Em seguida, remove os itens originais do mapeamento
        que continham a descrição completa. Após o ajuste do mapeamento,
        seleciona o valor informado em `data` e valida se o valor selecionado
        é válido. Caso o valor seja inválido (valor igual a "0"), é lançada
        uma exceção do tipo `SiscanInvalidFieldValueError`, informando os
        valores de opção disponíveis para o campo.

        Parâmetros
        ----------
        data : dict, opcional
            Dicionário contendo os dados do formulário, incluindo o campo
            'unidade_requisitante'.

        Exceções
        --------
        SiscanInvalidFieldValueError
            Lançada caso o valor selecionado para 'unidade_requisitante' seja
            inválido, ou não esteja entre as opções disponíveis (por exemplo,
            valor igual a "0").

        Exemplo
        -------
        ```
        self.seleciona_unidade_requisitante(
        {'unidade_requisitante': '0274267'})
        # Seleciona e valida a unidade requisitante com código CNES informado.
        ```

        Notas
        -----
        - O método atualiza o dicionário FIELDS_MAP['unidade_requisitante'],
          mantendo apenas o código CNES como chave, removendo os itens
          originais que continham  hífen e a descrição completa.
        - Este método depende das implementações de `load_select_options` e
          `select_value` para carregamento das opções do campo e seleção do
          valor, respectivamente.
        """
        nome_campo = "unidade_requisitante"
        self.load_select_options(nome_campo)

        # Atualiza o mapeamento de campos com os valores do select para obter
        # o código CNES do campo Unidade Requisitante.
        # Para cada chave no mapeamento, mantém apenas a parte antes do hífen
        # e.g., "0274267 - CENTRAL DE TELEATENDIMENTO SAUDE JA CURITIBA"
        # se torna "0274267"

        # Cria uma lista com os itens originais para evitar alteração durante
        # o loop
        for k, v in list(self.FIELDS_MAP[nome_campo].items()):
            key = f"{k.split('-')[0].strip()}"
            self.FIELDS_MAP[nome_campo][key] = v

            # Remove o item original que contém o hífen
            if v != "0":
                del self.FIELDS_MAP[nome_campo][k]

        text, value = self.select_value(nome_campo, data)
        if value == "0":
            raise SiscanInvalidFieldValueError(
                self.context,
                field_name=nome_campo,
                data=data,
                options_values=self.FIELDS_MAP[nome_campo].keys()
            )

    def selecionar_prestador(self, data: dict = None):
        """
        Seleciona e valida o campo 'prestador' a partir dos dados fornecidos.

        Este método realiza o carregamento das opções disponíveis para o campo
         'prestador', utiliza o valor presente em `data` para seleção e
        validação, e garante que o valor selecionado é válido conforme as
        opções disponíveis. Caso o valor selecionado seja inválido (igual a
        "0"), lança a exceção `SiscanInvalidFieldValueError`, informando os
        valores válidos para o campo.

        Parâmetros
        ----------
        data : dict, opcional
            Dicionário contendo os dados do formulário, incluindo o campo
            'prestador'.

        Exceções
        --------
        SiscanInvalidFieldValueError
            Lançada caso o valor selecionado para 'prestador' seja inválido,
            ou não esteja entre as opções disponíveis (por exemplo, valor
            igual a "0").

        Exemplo
        -------
        ```
        >>> self.selecionar_prestador({'prestador':
        'HOSPITAL ERASTO GAERTNER'})
        # Seleciona e valida o prestador informado.
        ```

        Notas
        -----
        - O método depende das implementações de `load_select_options` para
          carregar as opções do campo 'prestador' e de `select_value` para
          selecionar e validar o valor.
        - A validação considera como inválido o valor "0", que normalmente
          representa a opção  padrão "Selecione..." em campos select de
          formulários web.
        """
        nome_campo = "prestador"
        self.load_select_options(nome_campo)
        text, value = self.select_value(nome_campo, data)
        if value == "0":
            raise SiscanInvalidFieldValueError(
                self.context,
                field_name=nome_campo,
                data=data,
                options_values=self.FIELDS_MAP[nome_campo].keys()
            )

    def preencher(self, data: dict):
        """
        Preenche o formulário de novo exame de acordo com os campos informados.

        Parâmetros
        ----------
        campos : dict
            Dicionário onde a chave é o nome amigável do campo
            (ex: "Cartão SUS") e o valor é o dado a ser inserido.
        """
        self.validation(data)

        xpath = self._novo_exame(event_button=True)

        # 1o passo: Preenche o campo Cartão SUS e chama o
        # evento onblur do campo
        self.preencher_cartao_sus(
            numero=self.get_field_value("cartao_sus", data))

        # 2o passo: Define o tipo de exame para então poder habilitar
        # os campos de Prestador e Unidade Requisitante
        self.selecionar_tipo_exame(data)

        # 3o passo: Obtem os valores do campo select Unidade Requisitante,
        # atualiza o mapeamento de campos e preenche o campo
        self.seleciona_unidade_requisitante(data)

        # 4o passo: Obtem os valores do campo select Prestador,
        # atualiza o mapeamento de campos e preenche o campo
        self.selecionar_prestador(data)

        # 5o passo: Preenche os campos adicionais do formulário
        # Antes, monta o mapeamento de campos e os dados finais
        fields_map, data_final = self.mount_fields_map_and_data(
            data,
            RequisicaoExame.MAP_DATA_LABEL,
            suffix="",
        )

        # Remove os campos que já foram preenchidos
        fields_map.pop('unidade_requisitante')
        fields_map.pop('prestador')

        xpath.fill_form_fields(data_final, fields_map)
        self.take_screenshot("screenshot_03_requisicao_exame.png")
