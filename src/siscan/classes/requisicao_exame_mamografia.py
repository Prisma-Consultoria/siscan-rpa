import re

import logging

from src.siscan.exception import CartaoSusNotFoundError
from src.siscan.classes.requisicao_exame import RequisicaoExame
from src.siscan.schema.requisicao_mamografia_rastreamento_schema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE  # XPathElement
from src.utils import messages as msg

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
        "tipo_mamografia_de_rastreamento",
    ]

    FIELDS_MAP = {
        "tipo_de_mamografia": {
            "Diagnóstica": "01",
            "Rastreamento": "02",
        },
        "fez_cirurgia_de_mama": {
            "01": "S",
            "02": "N",
        },
    }

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(
            base_url,
            user,
            password,
            RequisicaoMamografiaRastreamentoSchema,
        )

        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=RequisicaoExameMamografia.MAP_SCHEMA_FIELDS
        )
        RequisicaoExameMamografia.MAP_DATA_LABEL = map_data_label
        fields_map.update(self.FIELDS_MAP)
        self.FIELDS_MAP = fields_map

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia
        data["tipo_exame_mama"] = "01"  # 01-Mamografia
        # Define o tipo de mamografia como "Rastreamento"
        data["tipo_de_mamografia"] = "Rastreamento"  # 02-Rastreamento

        super().validation(data)

    def get_map_label(self) -> dict[str, tuple[str, str, str]]:
        """
        Retorna o mapeamento de campos do formulário com seus respectivos
        labels e tipos, específico para o exame de Mamografia.
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

    async def preencher_tem_nodulo_ou_caroco_na_mama(self, data: dict):
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
        await self.select_value(nome_campo, {nome_campo: option_values})

    async def preencher_fez_mamografia_alguma_vez(self, data: dict):
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

    async def preencher_fez_radioterapia_na_mama_ou_no_plastao(self, data: dict):
        # Para "FEZ RADIOTERAPIA NA MAMA OU NO PLASTRÃO?"
        _, value = await self.select_value(
            "fez_radioterapia_na_mama_ou_no_plastrao", data
        )
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

    async def preencher_fez_cirurgia_cirurgica(self, data: dict):
        # Para "FEZ CIRURGIA DE MAMA?"
        _, value = await self.select_value("fez_cirurgia_de_mama", data)
        if value == "S":
            await self.preencher_ano_cirurgia(data)

    async def preencher_tipo_mamografia(self, data: dict):
        text, _ = await self.select_value("tipo_de_mamografia", data)
        if text == "Rastreamento":
            await self.select_value("tipo_mamografia_de_rastreamento", data)

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

        await (await xpath_ctx.find_form_button("Avançar")).handle_click()

        await self.preecher_fez_mamografia_alguma_vez(data)
        await self.preencher_fez_radioterapia_na_mama_ou_no_plastao(data)
        await self.preencher_fez_cirurgia_cirurgica(data)
        await self.preencher_tipo_mamografia(data)

        # TODO
        # TOFIX, não seria para implementar self.preencher_tem_nodulo_ou_caroco_na_mama ?
        await self.select_value("tem_nodulo_ou_caroco_na_mama", data)
        data.pop("tem_nodulo_ou_caroco_na_mama")

        fields_map, data_final = self.mount_fields_map_and_data(
            data,
            RequisicaoExameMamografia.MAP_DATA_LABEL,
            suffix="",
        )
        await xpath_ctx.fill_form_fields(data_final, fields_map)

        await self.take_screenshot("screenshot_04_requisicao_exame_mamografia.png")

    async def preencher_ano_cirurgia(self, data: dict):
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

RequisicaoExameMamografia.MAP_SCHEMA_FIELDS = (