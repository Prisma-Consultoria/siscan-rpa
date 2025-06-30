import logging


from src.siscan.classes.requisicao_exame import RequisicaoExame
from src.siscan.classes.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE  # XPathElement


from src.siscan.schema.requisicao_mamografia_diagnostica_schema import (
    RequisicaoMamografiaDiagnosticaSchema,
)
from src.siscan.schema.requisicao_mamografia_schema import RequisicaoMamografiaSchema

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaDiagnostica(RequisicaoExameMamografia):
    """Preenche a solicitação de mamografia do tipo diagnóstica."""

    def __init__(self, base_url: str, user: str, password: str):
        # Inicializa com o schema específico para mamografia diagnóstica
        RequisicaoExame.__init__(
            self,
            base_url,
            user,
            password,
            RequisicaoMamografiaDiagnosticaSchema,
        )

        base_fields = set(RequisicaoMamografiaSchema.model_fields.keys())
        diag_fields = set(RequisicaoMamografiaDiagnosticaSchema.model_fields.keys())
        RequisicaoExameMamografiaDiagnostica.MAP_SCHEMA_FIELDS = sorted(
            diag_fields - base_fields
        )

        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=self.MAP_SCHEMA_FIELDS
        )

        RequisicaoExameMamografiaDiagnostica.MAP_DATA_LABEL = map_data_label
        fields_map.update(self.FIELDS_MAP)
        self.FIELDS_MAP = fields_map

    def get_map_label(self) -> dict[str, tuple[str, str, str]]:
        """Retorna o mapeamento de campos específico deste exame."""
        map_label = {
            **RequisicaoExameMamografiaDiagnostica.MAP_DATA_LABEL,
        }
        map_label.update(super().get_map_label())
        return map_label

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia Diagnóstica
        data["tipo_exame_mama"] = "01"
        data["tipo_de_mamografia"] = "Diagnóstica"

        # Chama validação da classe base "RequisicaoExame"
        # RequisicaoExame.validation(self, data)

        return data

    async def preencher(self, data: dict):
        """
        Preenche o formulário de requisição de exame com os dados fornecidos.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário.
        """

        logger.debug("Iniciando preenchimento da requisição de mamografia diagnóstica")
        # Preenche os campos comuns do formulário
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        await RequisicaoExame.preencher(self, data)

        xpath_ctx = await XPE.create(
            self.context
        )  # TOFIX Não faz setido criar um xpath apenas com o contexto

        # TODO Código repetido, utilizar classe do RequisicaoExameMamografia posteriormente
        await (await xpath_ctx.find_form_button("Avançar")).handle_click()

        await RequisicaoExameMamografia.preencher_fez_mamografia_alguma_vez(self, data)
        await (
            RequisicaoExameMamografia.preencher_fez_radioterapia_na_mama_ou_no_plastao(
                self, data
            )
        )
        await RequisicaoExameMamografia.preencher_fez_cirurgia_cirurgica(self, data)
        await RequisicaoExameMamografia.preencher_tipo_mamografia(self, data)

        await self.select_value("tem_nodulo_ou_caroco_na_mama", data)
        data.pop("tem_nodulo_ou_caroco_na_mama")
        # print("Preenchendo achados de exame clínico")
        # await self.preencher_achados_exame_clinico(data)
        # logger.debug("Preenchendo controle radiológico de lesão categoria 3")
        # await self.preencher_controle_radiologico_lesao_categoria_3(data)
        # logger.debug("Preenchendo lesão de diagnóstico de câncer")
        # await self.preencher_lesao_diagnostico_cancer(data)
        # logger.debug("Preenchendo avaliação de resposta à quimioterapia")
        # await self.preencher_avaliacao_resposta_quimioterapia(data)
        # logger.debug("Preenchendo revisão de mamografia de outra instituição")
        # await self.preencher_revisao_mamografia_outra_instituicao(data)
        # logger.debug("Preenchendo controle de lesão pós-biópsia PAAF benigna")
        # await self.preencher_controle_lesao_pos_biopsia_paaf_benigna(data)

    async def _check_checkbox_by_id(self, element_id: str):
        """Marca um checkbox identificando pelo atributo id."""
        xpath = await XPE.create(self.context, xpath=f"//input[@id='{element_id}']")
        locator = await xpath.wait_and_get()
        if not await locator.is_checked():
            await locator.check(force=True)
        xpath.reset()

    async def _preencher_grupo(
        self,
        data: dict,
        campo_grupo: str,
        prefixo: str,
        element_id: str,
    ):
        """Preenche um grupo de campos ativado por checkbox."""
        sub_campos = [k for k in list(data.keys()) if k.startswith(prefixo)]
        if not data.get(campo_grupo) and not sub_campos:
            return

        await self._check_checkbox_by_id(element_id)
        data.pop(campo_grupo, None)

        if sub_campos:
            sub_data = {k: data[k] for k in sub_campos}
            fields_map, data_final = self.mount_fields_map_and_data(
                sub_data,
                RequisicaoExameMamografiaDiagnostica.MAP_DATA_LABEL,
                suffix="",
            )
            xpath_ctx = await XPE.create(self.context)
            await xpath_ctx.fill_form_fields(data_final, fields_map)
            for k in sub_campos:
                data.pop(k, None)

    async def preencher_achados_exame_clinico(self, data: dict):
        """
        Preenche os achados do exame clínico de mama com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="achados_exame_clinico",
            prefixo="exame_clinico_mama",
            element_id="frm:achadosExameClinico",
        )

    async def preencher_controle_radiologico_lesao_categoria_3(self, data: dict):
        """
        Preenche o controle radiológico de lesão categoria 3 com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="controle_radiologico_lesao_categoria_3",
            prefixo="controle_radiologico_lesao_categoria_3",
            element_id="frm:controleRadiologicoLesao",
        )

    async def preencher_lesao_diagnostico_cancer(self, data: dict):
        """
        Preenche a lesão de diagnóstico de câncer com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="lesao_diagnostico_cancer",
            prefixo="lesao_diagnostico_cancer",
            element_id="frm:lesaoDiagnosticoCancer",
        )

    async def preencher_avaliacao_resposta_quimioterapia(self, data: dict):
        """
        Preenche a avaliação de resposta à quimioterapia com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="avaliacao_resposta_quimioterapia_neoadjuvante",
            prefixo="avaliacao_resposta_quimioterapia",
            element_id="frm:avaliacaoRespostaQuimioterapia",
        )

    async def preencher_revisao_mamografia_outra_instituicao(self, data: dict):
        """
        Preenche a revisão de mamografia de outra instituição com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="revisao_mamografia_outra_instituicao",
            prefixo="revisao_mamografia_outra_instituicao",
            element_id="frm:revisaoMamografia",
        )

    async def preencher_controle_lesao_pos_biopsia_paaf_benigna(self, data: dict):
        """
        Preenche o controle de lesão pós-biópsia PAAF benigna com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="controle_lesao_pos_biopsia_paaf_benigna",
            prefixo="controle_lesao_pos_biopsia_paaf_benigna",
            element_id="frm:controleLesao",
        )
