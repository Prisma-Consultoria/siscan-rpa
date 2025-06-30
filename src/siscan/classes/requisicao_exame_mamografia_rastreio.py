import re

import logging

from src.siscan.exception import CartaoSusNotFoundError
from src.siscan.classes.requisicao_exame import RequisicaoExame
from src.siscan.schema.RequisicaoMamografiaRastreamentoSchema import (
    RequisicaoMamografiaRastreamentoSchema,
)
from src.siscan.schema.RequisicaoMamografiaDiagnosticaSchema import (
    RequisicaoMamografiaDiagnosticaSchema,
)
from src.siscan.classes.requisicao_exame_mamografia import (
    RequisicaoExameMamografia,
)
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE  # XPathElement
from src.utils import messages as msg

logger = logging.getLogger(__name__)


class RequisicaoExameMamografiaRastreio(RequisicaoExameMamografia):
    pass