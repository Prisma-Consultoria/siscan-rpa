import logging

from typing import Type
from pydantic import BaseModel

from src.siscan.schema.requisicao_mamografia_rastreamento_schema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.siscan.schema.requisicao_mamografia_schema import RequisicaoMamografiaSchema
from src.siscan.classes.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.utils.SchemaMapExtractor import SchemaMapExtractor

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaRastreio(RequisicaoExameMamografia):
    def __init__(self, base_url: str, user: str, password: str, schema_model: Type[BaseModel] = RequisicaoMamografiaRastreamentoSchema):
        # Inicializa com o schema específico para mamografia de rastreio
        super().__init__(
            base_url,
            user,
            password,
            schema_model,
        )

        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            self.schema_model, fields=self.MAP_SCHEMA_FIELDS
        )

        RequisicaoExameMamografiaRastreio.MAP_DATA_LABEL = map_data_label
        fields_map.update(self.FIELDS_MAP)
        self.FIELDS_MAP = fields_map

    def get_map_label(self) -> dict[str, tuple[str, str, str]]:
        """Retorna o mapeamento de campos específico deste exame."""
        map_label = {
            **RequisicaoExameMamografiaRastreio.MAP_DATA_LABEL,
        }
        map_label.update(super().get_map_label())
        return map_label

    async def preencher(self, data: dict):
        await super().preencher(data)
        await self.select_value("tipo_mamografia_de_rastreamento", data)
        await self.take_screenshot("screenshot_05.png")


base_fields = set(RequisicaoMamografiaSchema.model_fields.keys())
diag_fields = set(RequisicaoMamografiaRastreamentoSchema.model_fields.keys())
RequisicaoExameMamografiaRastreio.MAP_SCHEMA_FIELDS = sorted(diag_fields - base_fields)
