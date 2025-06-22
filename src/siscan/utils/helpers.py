from playwright.sync_api import sync_playwright
from env import PRODUCTION, TAKE_SCREENSHOT

def _run_rpa(form_type, data):
    screenshots = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not PRODUCTION)
        page = browser.new_page()
        # TODO: implementar login no SISCAN usando CPF/senha de users db

        # TODO: navegar até o formulário e preencher campos com 'data'
        # Exemplo: page.fill("input[name=campo1]", data.get("campo1", ""))

        if not PRODUCTION and TAKE_SCREENSHOT:
            for i in range(1, 4):
                path = f"static/tmp/{form_type}_step{i}.png"
                page.screenshot(path=path)
                screenshots.append(path)

        if PRODUCTION:
            page.click("button[type=submit]")

        browser.close()

    return {"success": True, "screenshots": screenshots}