import pytest
import logging
from pathlib import Path

from src.siscan.requisicao_exame_mamografia import (
    RequisicaoExameMamografiaDiagnostica,
)
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD
from src.utils.validator import Validator
from src.siscan.context import SiscanBrowserContext

logger = logging.getLogger(__name__)


@pytest.mark.asyncio(loop_scope="session")
async def test_preencher_requisicao_mamografia_diagnostica():
    dados_path = Path("real_data_diagnostica.json")

    if not dados_path.exists():
        pytest.skip(f"Arquivo {dados_path} não encontrado.")

    if not SISCAN_USER or not SISCAN_PASSWORD:
        pytest.skip("Credenciais do SISCAN não configuradas")

    json_data = Validator.load_json(dados_path)

    req = RequisicaoExameMamografiaDiagnostica(
        base_url=SISCAN_URL, user=SISCAN_USER, password=SISCAN_PASSWORD
    )

    req._context = SiscanBrowserContext(headless=True)

    await req.authenticate()
    await req.preencher(json_data)

    informations = req.context.information_messages

    logger.info("Informações coletadas:")
    for key, messages in informations.items():
        logger.info(f"{key}: {', '.join(messages)}")

    await req.context.close()
