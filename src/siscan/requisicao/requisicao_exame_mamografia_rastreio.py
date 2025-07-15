#
# Subclasse de RequisicaoExameMamografia, focada na lógica para mamografia de
# rastreamento.
#
# Define campos e métodos específicos desse subtipo de requisição
# (preenchimento de tipo, rastreio, responsável pela coleta etc.)
#
import logging
from pydantic import BaseModel
from typing import Type, Any

from src.siscan.requisicao.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.siscan.schema import TipoDeMamografia
from src.siscan.schema.requisicao_mamografia_rastreamento_schema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.siscan.schema.requisicao_mamografia_schema import \
    RequisicaoMamografiaSchema
from src.utils.SchemaMapExtractor import SchemaMapExtractor

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaRastreio(RequisicaoExameMamografia):
    def __init__(
            self, base_url: str, user: str, password: str,
            schema_model: Type[BaseModel] = RequisicaoMamografiaRastreamentoSchema
    ):
        # Inicializa com o schema específico para mamografia de rastreio
        super().__init__(
            base_url,
            user,
            password,
            schema_model,
        )

        # Extrai o mapeamento dos labels e campos do schema informado
        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=self.MAP_SCHEMA_FIELDS
        )

        # Atualiza o mapeamento de labels da classe
        RequisicaoExameMamografiaRastreio.MAP_DATA_LABEL = map_data_label
        # Atualiza o dicionário de campos, mesclando com os campos já existentes
        fields_map.update(self.FIELDS_MAP)
        self.FIELDS_MAP = fields_map

    def get_map_label(self) -> dict[str, dict[str, Any]]:
        """Retorna o mapeamento de campos específico deste exame."""
        map_label = {
            **RequisicaoExameMamografiaRastreio.MAP_DATA_LABEL,
        }
        map_label.update(super().get_map_label())
        return map_label

    def validation(self, data: dict):
        # Define o tipo de exame como Mamografia de Rastreio
        data["tipo_de_mamografia"] = TipoDeMamografia.RASTREAMENTO.value
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


base_fields = set(RequisicaoMamografiaSchema.model_fields.keys())
diag_fields = set(RequisicaoMamografiaRastreamentoSchema.model_fields.keys())
RequisicaoExameMamografiaRastreio.MAP_SCHEMA_FIELDS = sorted(diag_fields - base_fields)
