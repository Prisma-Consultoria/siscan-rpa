from fastapi import FastAPI
from playwright.sync_api import sync_playwright
from env import PRODUCTION, TAKE_SCREENSHOT, get_db
from routes import router

app = FastAPI()

# Cria tabela de usuários se não existir
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
""")
conn.commit()
conn.close()

app.include_router(router)





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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
