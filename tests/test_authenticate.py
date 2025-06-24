from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.siscan.context import SiscanBrowserContext
from src.env import SISCAN_USER, SISCAN_PASSWORD, SISCAN_URL
import logging
import pytest

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_authenticate():
    requisicao = RequisicaoExameMamografia(
        base_url=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )
    # Use contexto headless para nao abrir janela durante testes
    requisicao._context = SiscanBrowserContext(
        base_url=SISCAN_URL,
        headless=False,
        timeout=15000,
    )

    await requisicao.authenticate()

    assert await requisicao.context.page.locator(
        'h1:text("SEJA BEM VINDO AO SISCAN")'
    ).is_visible()

    # Fechar navegador após o teste
    await requisicao.context.browser.close()
