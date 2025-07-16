#
# Especializa a RequisicaoExame para o exame de mamografia, implementando
# regras, validações e métodos específicos da mamografia (como seleção de
# tipo, dependências condicionais, campos adicionais do formulário).
#
# Organiza lógica própria de campos e mapeamento do formulário de mamografia
#
import logging

from src.siscan import messages as msg
from src.siscan.exception import CartaoSusNotFoundError, \
    SiscanInvalidFieldValueError
from src.siscan.requisicao.requisicao_exame import RequisicaoExame
from src.siscan.schema.requisicao_mamografia_schema import (
    RequisicaoMamografiaSchema,
)
from src.siscan.schema.requisicao_novo_exame_schema import (
    TipoExameMama,
)
from src.siscan.webpage.base import ensure_metadata_schema_fields
from src.siscan.webpage.xpath_constructor import \
    XPathConstructor as XPE  # XPathElement

logger = logging.getLogger(__name__)


class RequisicaoExameMamografia(RequisicaoExame):
    _schema_model = RequisicaoMamografiaSchema

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url, user, password)
        ensure_metadata_schema_fields(RequisicaoExameMamografia)

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia
        data["tipo_exame_mama"] = TipoExameMama.MAMOGRAFIA.value
        super().validation(data)


    async def selecionar_tipo_exame(self, data: dict):
        """
        Seleciona o tipo de exame como Mamografia.
        """
        await self.select_value("tipo_exame_mama", data)

    async def _preencher_fez_mamografia_alguma_vez(self, data: dict):
        await self.preencher_campo_dependente_multiplo(
            data,
            campo_chave="fez_mamografia_alguma_vez",
            condicoes_dependentes={
                "01": ["ano_que_fez_a_ultima_mamografia"],
            },
            label_dependentes={
                "ano_que_fez_a_ultima_mamografia": "Ano:",
            },
            erro_dependente_msg=msg.ANO_MAMOGRAFIA_REQUIRED,
        )

    async def _preencher_fez_radioterapia_na_mama_ou_no_plastao(self, data: dict):
        # Para "FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?"
        _, value = await self.select_value(
            "fez_radioterapia_na_mama_ou_no_plastrao", data
        )
        data.pop("fez_radioterapia_na_mama_ou_no_plastrao", None)
        if value == "01":
            # Para "RADIOTERAPIA - LOCALIZAÇÃO"
            await self.preencher_campo_dependente_multiplo(
                data,
                campo_chave="radioterapia_localizacao",
                condicoes_dependentes={
                    "01": ["ano_da_radioterapia_esquerda"],
                    "02": ["ano_da_radioterapia_direita"],
                    "03": [
                        "ano_da_radioterapia_direita",
                        "ano_da_radioterapia_esquerda",
                    ],
                },
                label_dependentes={
                    "ano_da_radioterapia_direita": "Ano da Radioterapia - Direita:",
                    "ano_da_radioterapia_esquerda": "Ano da Radioterapia - Esquerda:",
                },
                erro_dependente_msg=msg.ANO_RADIOTERAPIA_REQUIRED,
            )

    async def _preencher_ano_cirurgia(self, data: dict):
        for field_name in RequisicaoMamografiaSchema.FIELDS_PROCEDIMENTOS_CIRURGICOS:
            if data.get(field_name):

                xpath = await XPE.create(self.context,
                                         xpath=self.get_field_xpath(field_name)
                                         )
                await xpath.handle_fill(
                    self.get_field_value(field_name, data),
                    self.get_field_type(field_name),
                )
                data.pop(field_name)

    async def _preencher_fez_cirurgia_cirurgica(self, data: dict):
        # Para "FEZ CIRURGIA DE MAMA?"
        _, value = await self.select_value("fez_cirurgia_de_mama",
                                           data)
        data.pop("fez_cirurgia_de_mama", None)
        if value == "S":
            await self._preencher_ano_cirurgia(data)

    async def _seleciona_responsavel_coleta(self, data: dict | None = None):
        """
        Seleciona e valida a unidade requisitante a partir dos dados fornecidos.
        """
        nome_campo = "cns_responsavel_coleta"
        await self.load_select_options(nome_campo)

        # Atualiza o mapeamento de campos usando apenas o código CNES após do hífen.
        for k, v in list(self.FIELDS_VALUE_MAP[nome_campo].items()):
            key = f"{k.split('-')[-1].strip()}"
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

    async def preencher(self, data: dict):
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
            raise CartaoSusNotFoundError(
                self.context,
                msg.CARTAO_SUS_NAO_INFORMADO,
            )

        await super().preencher(data)

        xpath_ctx = await XPE.create(
            self.context
        )  # TOFIX Não faz setido criar um xpath apenas com o contexto

        # 1o passo: após preenchido os dados básicos do formulário de
        # "Novo Exame", clica no botão "Avançar" para ir para o
        # formulário de requisição de mamografia
        await (await xpath_ctx.find_form_button("Avançar")).handle_click()
        await self.wait_page_ready()

        # 2o passo: Preenche os campos específicos do formulário
        await self.fill_form_field("num_prontuario", data, suffix="")
        await self.select_value(
            "tem_nodulo_ou_caroco_na_mama", data)
        await self.select_value(
            "apresenta_risco_elevado_para_cancer_mama", data)
        await self.select_value(
            "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional", data)
        await self._preencher_fez_mamografia_alguma_vez(data)
        await self._preencher_fez_radioterapia_na_mama_ou_no_plastao(data)
        await self._preencher_fez_cirurgia_cirurgica(data)

        await self.fill_form_field("data_da_solicitacao", data)

        await self.take_screenshot("screenshot_04_requisicao_exame_mamografia.png")



