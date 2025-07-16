#
# Especializa a RequisicaoExame para o exame de mamografia, implementando
# regras, validações e métodos específicos da mamografia (como seleção de
# tipo, dependências condicionais, campos adicionais do formulário).
#
# Organiza lógica própria de campos e mapeamento do formulário de mamografia
#
import logging
import re
from pydantic import BaseModel
from typing import Type

from src.siscan.exception import CartaoSusNotFoundError, \
    SiscanInvalidFieldValueError
from src.siscan.requisicao.requisicao_exame import RequisicaoExame
from src.siscan.schema.requisicao_mamografia_schema import (
    RequisicaoMamografiaSchema,
)
from src.siscan.schema.requisicao_novo_exame_schema import (
    RequisicaoNovoExameSchema, TipoExameMama,
)
from src.siscan.webpage.xpath_constructor import \
    XPathConstructor as XPE  # XPathElement
from src.siscan import messages as msg
from src.utils.SchemaMapExtractor import SchemaMapExtractor

logger = logging.getLogger(__name__)


class RequisicaoExameMamografia(RequisicaoExame):
    # manual https://www.inca.gov.br/sites/ufu.sti.inca.local/files/media/document/manual_siscan_modulo2_2021_1.pdf
    FIELDS_MAP = {
        "fez_cirurgia_de_mama": {
            "01": "S",
            "02": "N",
        },
    }

    def __init__(
        self,
        base_url: str,
        user: str,
        password: str,
        schema_model: Type[BaseModel] = RequisicaoMamografiaSchema,
    ):
        super().__init__(
            base_url,
            user,
            password,
            schema_model,
        )

        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=RequisicaoExameMamografia.MAP_SCHEMA_FIELDS
        )

        RequisicaoExameMamografia.MAP_DATA_LABEL = map_data_label
        fields_map.update(self.FIELDS_MAP)
        self.FIELDS_MAP = fields_map

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia
        data["tipo_exame_mama"] = TipoExameMama.MAMOGRAFIA.value
        super().validation(data)

    def get_map_label(self) -> dict[str, dict[str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos labels e tipos, específico para o exame de Mamografia.
        """
        map_label = {
            **RequisicaoExameMamografia.MAP_DATA_LABEL,
        }
        map_label.update(super().get_map_label())
        return map_label

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
        anos_procedimentos = [
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
        ]

        for campo_nome in anos_procedimentos:
            lado = "direita" if "direita" in campo_nome else "esquerda"

            label_raw = self.get_field_label(campo_nome)
            # remove texto entre parênteses, remove "(Direita)" ou "(Esquerda)"
            label = re.sub(r"\s*\(.*?\)\s*", "", label_raw).strip()

            base_xpath = (
                f"//fieldset[legend[normalize-space(text())='OPÇÕES DE CIRURGIA']]"
                f"//label[normalize-space(text())='{label}']/parent::div"
            )
            if lado == "direita":
                base_xpath = (
                    f"{base_xpath}/preceding-sibling::div[1]//input[@type='text']"
                )
            elif lado == "esquerda":
                base_xpath = (
                    f"{base_xpath}/following-sibling::div[1]//input[@type='text']"
                )
            else:
                raise ValueError("O parâmetro 'lado' deve ser 'direita' ou 'esquerda'.")

            xpath = await XPE.create(self.context, xpath=base_xpath)
            await xpath.handle_fill(
                self.get_field_value(campo_nome, data),
                self.get_field_type(campo_nome),
            )
            data.pop(campo_nome)

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
        for k, v in list(self.FIELDS_MAP[nome_campo].items()):
            key = f"{k.split('-')[-1].strip()}"
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

base_fields = set(RequisicaoNovoExameSchema.model_fields.keys())
diag_fields = set(RequisicaoMamografiaSchema.model_fields.keys())
RequisicaoExameMamografia.MAP_SCHEMA_FIELDS = sorted(diag_fields - base_fields)

