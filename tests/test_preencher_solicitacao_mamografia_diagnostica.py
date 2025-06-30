import pytest
import logging
from pathlib import Path

from src.siscan.classes.requisicao_exame_mamografia_diagnostica import (
    RequisicaoExameMamografiaDiagnostica,
)
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD
from src.utils.validator import Validator
from src.siscan.context import SiscanBrowserContext

logger = logging.getLogger(__name__)


@pytest.mark.asyncio(loop_scope="session")
async def test_preencher_requisicao_mamografia_diagnostica(headless: bool):
    dados_path = Path("real_data_diagnostica.json")

    if not dados_path.exists():
        raise FileNotFoundError(f"Arquivo {dados_path} não encontrado.")

    json_data = Validator.load_json(dados_path)

    req = RequisicaoExameMamografiaDiagnostica(
        base_url=SISCAN_URL, user=SISCAN_USER, password=SISCAN_PASSWORD
    )

    req._context = SiscanBrowserContext(headless=headless)

    await req.authenticate()
    await req.preencher(json_data)

    await req.context.close()
