from playwright.async_api import async_playwright
from ..env import PRODUCTION, TAKE_SCREENSHOT

async def run_rpa(form_type, data):
    """Executa o fluxo do RPA utilizando Playwright assíncrono."""
    screenshots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # TODO: implementar login no SISCAN usando CPF/senha de users db

        # TODO: navegar até o formulário e preencher campos com 'data'
        # Exemplo: page.fill("input[name=campo1]", data.get("campo1", ""))

        if not PRODUCTION and TAKE_SCREENSHOT:
            for i in range(1, 4):
                path = f"static/tmp/{form_type}_step{i}.png"
                await page.screenshot(path=path)
                screenshots.append(path)

        if PRODUCTION:
            await page.click("button[type=submit]")

        await browser.close()

    return {"success": True, "screenshots": screenshots}

