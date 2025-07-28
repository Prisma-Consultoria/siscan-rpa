#
# Subclasse de RequisicaoExameMamografia, focada na lógica para mamografia
# diagnóstica.
#
# Implementa métodos próprios para preenchimento de campos/grupos de achados
# clínicos, controle radiológico, avaliação de resposta a tratamentos,
# revisão de outras instituições etc.
#
import logging
from typing import List

from src.siscan.requisicao.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.siscan.schema.requisicao_mamografia_diagnostica_schema import (
    RequisicaoMamografiaDiagnosticaSchema,
)
from src.siscan.schema.types import YesNo
from src.siscan.webpage.base import ensure_metadata_schema_fields
from src.siscan.webpage.xpath_constructor import \
    XPathConstructor as XPE  # XPathElement

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaDiagnostica(RequisicaoExameMamografia):
    """Preenche a solicitação de mamografia do tipo diagnóstica."""
    _schema_model = RequisicaoMamografiaDiagnosticaSchema

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url, user, password)
        ensure_metadata_schema_fields(RequisicaoExameMamografiaDiagnostica)

    def validation(self, data: dict):
        super().validation(data)
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

        await super().preencher(data)

        # 3o passo: preencher os campos específicos de diagnóstico
        await self.fill_form_field("tipo_de_mamografia",
                                   data, suffix="")

        print("Preenchendo achados de exame clínico")
        await self.preencher_achados_exame_clinico(data)
        logger.debug("Preenchendo controle radiológico de lesão categoria 3")
        await self.preencher_controle_radiologico_lesao_categoria_3(data)
        logger.debug("Preenchendo lesão de diagnóstico de câncer")
        await self.preencher_lesao_diagnostico_cancer(data)
        logger.debug("Preenchendo avaliação de resposta à quimioterapia")
        await self.preencher_avaliacao_resposta_quimioterapia(data)
        logger.debug("Preenchendo revisão de mamografia de outra instituição")
        await self.preencher_revisao_mamografia_outra_instituicao(data)
        logger.debug("Preenchendo controle de lesão pós-biópsia PAAF benigna")
        await self.preencher_controle_lesao_pos_biopsia_paaf_benigna(data)

        await self._seleciona_responsavel_coleta(data)

        await self.take_screenshot("screenshot_05_mamografia_diagnostica.png")

    async def _check_checkbox_by_XP(self, x_xpath: str):
        """Marca um checkbox identificando pelo xpath."""
        xpath = await XPE.create(self.context, xpath=x_xpath)
        locator = await xpath.wait_and_get()
        if not await locator.is_checked():
            await locator.check(force=True)
        xpath.reset()

    async def _preencher_grupo(
        self,
        data: dict,
        campo_grupo: str,
        prefixo: str,
    ):
        """Preenche um grupo de campos ativado por checkbox."""
        sub_campos = [k for k in list(data.keys()) if k.startswith(prefixo)]
        value = data.get(campo_grupo, YesNo.NAO.value)
        if value == YesNo.NAO.value and not sub_campos:
            return

        await self._check_checkbox_by_XP(
            self.get_field_metadata(campo_grupo).get('xpath'))
        data.pop(campo_grupo, None)

        if sub_campos:
            sub_data = {k: data[k] for k in sub_campos}
            await self.fill_form_fields(
                sub_data,
                RequisicaoExameMamografiaDiagnostica.get_fields_mapping(),
                suffix=""
            )
            for k in sub_campos:
                data.pop(k, None)

    async def preencher_achados_exame_clinico(self, data: dict):
        """
        Preenche os achados do exame clínico de mama com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_achados_exame_clinico",
            prefixo="exame_clinico_mama",
        )

    async def preencher_controle_radiologico_lesao_categoria_3(self, data: dict):
        """
        Preenche o controle radiológico de lesão categoria 3 com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_controle_radiologico_lesao_categoria_3",
            prefixo="controle_radiologico_lesao_categoria_3",
        )

    async def preencher_lesao_diagnostico_cancer(self, data: dict):
        """
        Preenche a lesão de diagnóstico de câncer com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_lesao_diagnostico_cancer",
            prefixo="lesao_diagnostico_cancer",
        )

    async def preencher_avaliacao_resposta_quimioterapia(self, data: dict):
        """
        Preenche a avaliação de resposta à quimioterapia com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_avaliacao_resposta_quimioterapia_neoadjuvante",
            prefixo="avaliacao_resposta_quimioterapia",
        )

    async def preencher_revisao_mamografia_outra_instituicao(self, data: dict):
        """
        Preenche a revisão de mamografia de outra instituição com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_revisao_mamografia_outra_instituicao",
            prefixo="revisao_mamografia_outra_instituicao",
        )

    async def preencher_controle_lesao_pos_biopsia_paaf_benigna(self, data: dict):
        """
        Preenche o controle de lesão pós-biópsia PAAF benigna com base nos dados fornecidos.
        """
        await self._preencher_grupo(
            data,
            campo_grupo="grupo_controle_lesao_pos_biopsia_paaf_benigna",
            prefixo="controle_lesao_pos_biopsia_paaf_benigna",
        )
