import logging

from typing import Optional
from playwright.sync_api import sync_playwright, Browser, Page

logger = logging.getLogger(__name__)

class SiscanBrowserContext:
    """
    Centraliza as configurações de contexto e inicialização do Playwright para o SIScan.

    Atributos
    ---------
    url_base : str
        URL base do SIScan.
    headless : bool
        Define se o navegador será executado em modo headless.
    timeout : int
        Timeout padrão (ms) para operações de navegação.

    """

    def __init__(
        self,
        url_base: str = "https://siscan.saude.gov.br/",
        headless: bool = True,
        timeout: int = 10000
    ):
        self._url_base = url_base
        self.headless = headless
        self._timeout = timeout

        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        
        self._information_messages: dict[str, list[str]] = {}

    @property
    def url_base(self) -> str:
        """
        Retorna a URL base do SIScan.
        """
        return self._url_base

    #@property
    def timeout(self) -> int:
        """
        Retorna o timeout padrão para operações de navegação.
        """
        return self._timeout

    @property
    def information_messages(self) -> dict[str, list[str]]:
        """
        Retorna os informes coletados da popup de mensagens informativas.
        """
        return self._information_messages

    @property
    def browser(self) -> Browser:
        """
        Retorna o navegador Playwright atual. Se não estiver inicializado, chama get_browser_and_page.
        """
        if self._browser is None:
            self._browser, self._page = self.get_browser_and_page()
        return self._browser

    @property
    def page(self) -> Page:
        """
        Retorna a página Playwright atual. Se não estiver inicializada, chama get_browser_and_page.
        """
        if self._page is None:
            self._browser, self._page = self.get_browser_and_page()
        return self._page

    def close(self):
        if self._browser:
            self._browser.close()
            self._browser = None
            self._page = None

    def goto(self, path: str, wait_until: str = "load", **kwargs) -> Page:
        """
        Navega para o caminho informado, relativo à url_base, utilizando a página Playwright.

        Parâmetros
        ----------
        path : str
            Caminho relativo, por exemplo '/login'.
        wait_until : str
            Estratégia de espera após navegação ('load', 'domcontentloaded', etc.)
        kwargs : dict
            Parâmetros adicionais para page.goto.

        Retorno
        -------
        Page
            A página Playwright navegada para o URL construído.
        """
        if not self._page:
            self.get_browser_and_page()
        url = self._url_base.rstrip('/') + '/' + path.lstrip('/')
        logger.debug(f"Navegando para: {url}")
        self._page.goto(url, wait_until=wait_until, **kwargs)

        return self._page

    def get_browser_and_page(self) -> tuple:
        if self._browser and self._page:
            return self._browser, self._page
        playwright = sync_playwright().start()
        self._browser = playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        self._page.goto(self._url_base, wait_until="load")
        return self._browser, self._page

    def collect_information_popup(self) -> dict[str, list[str]]:
        """
        Coleta todos os informes da popup, estruturando como {data: [linhas de texto, ...]}, e fecha a popup.

        Retorno
        -------
        dict
            Dicionário {data: [lista de linhas de conteúdo]}
        """
        context = self._page.context
        popup = None
        for current_page in context.pages:
            if current_page != self._page and "popupMensagensInformativas.jsf" in current_page.url:
                popup = current_page
                break
        if not popup:
            return {}

        popup.wait_for_load_state("domcontentloaded")

        # Para cada tr da tabela de informes:
        trs = popup.locator('table#listaMensagens tr.rich-table-row')

        for i in range(trs.count()):
            tr = trs.nth(i)

            # Localiza o <span> que está após o <label> (na mesma linha do "Informe de")
            date_elem = tr.locator('p[align="center"] > b > span')
            if date_elem.count() == 0:
                continue
            notice_date = date_elem.first.inner_text().strip()

            subject_elem = tr.locator("p").nth(1)
            notice_subject = subject_elem.inner_text().strip()

            # Todas as linhas de texto do conteúdo
            lines = []

            # Coleta todos os <div id="divDesc"> > <p>
            ps = tr.locator('div#divDesc p')
            for j in range(ps.count()):
                texto = ps.nth(j).inner_text().strip()
                if texto:
                    lines.append(texto)
            self._information_messages[(notice_date, notice_subject)] = lines

        # Fecha a popup após coleta
        popup.close()
        return self._information_messages

