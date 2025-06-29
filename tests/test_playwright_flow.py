import logging
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, Page

from src.utils.validator import Validator
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="session")
async def playwright_page():
    """Cria contexto Playwright manualmente e autentica no SIScan."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(base_url=SISCAN_URL)
        page = await context.new_page()

        await page.goto("/login.jsf")
        await page.get_by_label("E-mail").fill(SISCAN_USER)
        await page.get_by_label("Senha").fill(SISCAN_PASSWORD)
        await page.get_by_role("button", name="Acessar").click()
        await page.wait_for_selector("text=SEJA BEM VINDO AO SISCAN")

        # Navega pelo menu até a opção Novo Exame
        await page.locator(
            ".rich-ddmenu-label .rich-label-text-decor",
            has_text="EXAME",
        ).first.hover()
        await page.locator(
            ".rich-menu-item-label",
            has_text="GERENCIAR EXAME",
        ).click()
        await page.locator("a.form-button", has_text="Novo Exame").click()
        await page.wait_for_selector("label:has-text('Unidade Requisitante')")

        yield page
        await browser.close()


@pytest.mark.asyncio(loop_scope="session")
async def test_preencher_campos_metodo_playwright(
    playwright_page: Page, fake_json_rastreio_file
):
    page = playwright_page
    data = Validator.load_json(fake_json_rastreio_file)

    await page.get_by_label("Ponto de Referência").fill(data["ponto_de_referencia"])
    await page.get_by_label("Apelido").fill(data["apelido"])
    await page.get_by_label("Mamografia").check()

    element = await page.query_selector("select#frm\\:escolaridade")
    await element.select_option(label="Ensino Fundamental Completo")

    option_locator = page.locator(
        'select#frm\\:unidadeSaudeCoordenacaoMunicipal option[value="1"]'
    )
    await option_locator.wait_for(state="attached", timeout=5000)

    select = page.get_by_label("Unidade Requisitante")
    await select.select_option(
        label="0274267 - CENTRAL DE TELEATENDIMENTO SAUDE JA CURITIBA"
    )

    await page.screenshot(path="screenshot.png")
