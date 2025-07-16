#
# Subclasse de RequisicaoExameMamografia, focada na lógica para mamografia de
# rastreamento.
#
# Define campos e métodos específicos desse subtipo de requisição
# (preenchimento de tipo, rastreio, responsável pela coleta etc.)
#
import logging
from typing import List

from src.siscan.requisicao.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.siscan.schema.requisicao_mamografia_rastreamento_schema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.siscan.webpage.base import ensure_metadata_schema_fields

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaRastreio(RequisicaoExameMamografia):
    _schema_model = RequisicaoMamografiaRastreamentoSchema

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url, user, password)
        ensure_metadata_schema_fields(RequisicaoExameMamografiaRastreio)

    def validation(self, data: dict):
        super().validation(data)
        return data

    async def preencher(self, data: dict):
        self.validation(data)
        await super().preencher(data)

        # 3o passo: preencher os campos específicos de rastreio
        await self.fill_form_field("tipo_de_mamografia",
                                   data, suffix="")
        await self.fill_form_field(
            "tipo_mamografia_de_rastreamento", data, suffix="")

        await self._seleciona_responsavel_coleta(data)

        await self.take_screenshot("screenshot_05_mamografia_rastreamento.png")



