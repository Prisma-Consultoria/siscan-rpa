from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.siscan.context import SiscanBrowserContext
from src.env import SISCAN_USER, SISCAN_PASSWORD, SISCAN_URL

def test_authenticate():

    requisicao = RequisicaoExameMamografia(
        url_base=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )
    # Use contexto headless para nao abrir janela durante testes
    requisicao._context = SiscanBrowserContext(
        url_base=requisicao._url_base,
        headless=True,
        timeout=15000,
    )

    requisicao.authenticate()
    assert requisicao.context.page.locator(
        'h1:text("SEJA BEM VINDO AO SISCAN")'
    ).is_visible()
