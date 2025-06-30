import re

import logging

from src.siscan.exception import CartaoSusNotFoundError
from src.siscan.classes.requisicao_exame import RequisicaoExame
from src.siscan.schema.requisicao_mamografia_rastreamento_schema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.siscan.schema.requisicao_mamografia_schema import RequisicaoMamografiaSchema
from src.siscan.classes.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE  # XPathElement
from src.utils import messages as msg

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaRastreio(RequisicaoExameMamografia):
    def __init__(self, base_url: str, user: str, password: str):
        # Inicializa com o schema específico para mamografia de rastreio
        RequisicaoExame.__init__(
            self,
            base_url,
            user,
            password,
            RequisicaoMamografiaRastreamentoSchema,
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
        print("+" * 20)
        print("+" * 20)
        print(RequisicaoExameMamografia(base_url=self._base_url, user=self._user, password=self._password).get_map_label())
        print(super().get_map_label())
        print(RequisicaoExameMamografiaRastreio.MAP_DATA_LABEL)
        print(RequisicaoExameMamografia.MAP_SCHEMA_FIELDS)
        print("+" * 20)
        print("+" * 20)
        return map_label

    async def preencher(self, data: dict):
        await RequisicaoExameMamografia.preencher(self, data)
        await self.select_value("tipo_mamografia_de_rastreamento", data)


base_fields = set(RequisicaoMamografiaSchema.model_fields.keys())
diag_fields = set(RequisicaoMamografiaRastreamentoSchema.model_fields.keys())
RequisicaoExameMamografiaRastreio.MAP_SCHEMA_FIELDS = sorted(diag_fields - base_fields)
