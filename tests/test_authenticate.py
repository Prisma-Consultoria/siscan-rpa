import os
import pytest
from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.siscan.context import SiscanBrowserContext


def test_authenticate(monkeypatch):
    monkeypatch.setenv("SISCAN_USER", "dummy@example.com")
    monkeypatch.setenv("SISCAN_PASSWORD", "dummy")

    requisicao = RequisicaoExameMamografia(
        url_base=os.getenv("SISCAN_URL", "https://siscan.saude.gov.br/"),
        user=os.getenv("SISCAN_USER"),
        password=os.getenv("SISCAN_PASSWORD"),
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
