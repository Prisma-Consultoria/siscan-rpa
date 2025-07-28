import pytest
import logging
from pathlib import Path

from src.siscan.requisicao.requisicao_exame_mamografia_rastreio import (
    RequisicaoExameMamografiaRastreio,
)
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD
from src.utils.validator import Validator
from src.siscan.webpage.context import SiscanBrowserContext

logger = logging.getLogger(__name__)


@pytest.mark.asyncio(loop_scope="session")
async def test_preencher_requisicao_mamografia_rastreamento(headless: bool):
    # Você precisa ter um arquivo JSON com dados reais apra preencher o
    # formulário, certifique-se de que o caminho está correto.
    dados_path = Path("real_data_rastreamento.json")

    # Verifica se o arquivo existe
    if not dados_path.exists():
        raise FileNotFoundError(f"Arquivo {dados_path} não encontrado.")

    json_data = Validator.load_json(dados_path)

    req = RequisicaoExameMamografiaRastreio(
        base_url=SISCAN_URL, user=SISCAN_USER, password=SISCAN_PASSWORD
    )

    req._context = SiscanBrowserContext(headless=headless)

    # Preencher chama o método de autenticação, pois antes faz-se necessário
    # verificar se os dados recebidos são válidos antes de inicializar o
    # navegador e preencher a requisição.
    await req.preencher(json_data)

    informations = req.context.information_messages

    logger.info("Informações coletadas:")
    for key, messages in informations.items():
        logger.info(f"{key}: {', '.join(messages)}")

    await req.context.close()
