from src.siscan.classes.requisicao_exame_mamografia_rastreio import (
    RequisicaoExameMamografiaRastreio,
)
from src.siscan.context import SiscanBrowserContext
from src.env import SISCAN_USER, SISCAN_PASSWORD, SISCAN_URL
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_authenticate(headless: bool):
    req = RequisicaoExameMamografiaRastreio(
        base_url=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )
    # Use contexto headless para nao abrir janela durante testes
    req._context = SiscanBrowserContext(
        base_url=SISCAN_URL,
        headless=headless,
        timeout=15000,
    )

    await req.authenticate()

    assert (
        await (await req.context.page)
        .locator('h1:text("SEJA BEM VINDO AO SISCAN")')
        .is_visible()
    )

    # Fechar navegador após o teste
    await (await req.context.browser).close()
