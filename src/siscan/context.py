import logging
import asyncio
from typing import Optional
from src.utils import messages as msg
from playwright.async_api import async_playwright, Browser, Page


logger = logging.getLogger(__name__)


class SiscanBrowserContext:
    """
    Centraliza as configurações de contexto e inicialização do Playwright para o SISCAN.
    """

    def __init__(
        self,
        base_url: str = "https://siscan.saude.gov.br/",
        headless: bool = True,
        timeout: int = 10000,
    ):
        self._base_url = base_url
        self._timeout = timeout
        self.headless = headless

        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

        self._information_messages: dict[str, list[str]] = {}

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base do SIScan.
        """
        return self._base_url

    # @property
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
    async def browser(self) -> Browser:
        """
        Retorna o navegador Playwright atual. Se não estiver inicializado, chama startup.
        """
        if self._browser is None:
            self._browser, self._page = await self.startup()
        return self._browser

    @property
    async def page(self) -> Page:
        """
        Retorna a página Playwright atual. Se não estiver inicializada, chama startup.
        """
        if self._page is None:
            self._browser, self._page = await self.startup()
        return self._page

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None
        if getattr(self, "_playwright", None):
            await self._playwright.stop()
            self._playwright = None

    async def handle_goto(self, path: str, **kwargs) -> Page:
        if not self._page:
            await self.startup()
        url = self._base_url.rstrip("/") + "/" + path.lstrip("/")
        logger.debug(f"Navegando para: {url}")
        if self._page:
            await self._page.goto(url, **kwargs)
        else:
            raise Exception(msg.CONTEXT_NOT_INITIALIZED)

        return self._page

    async def startup(self) -> tuple[Browser, Page]:
        if self._browser and self._page:
            return self._browser, self._page

        async def _launch():
            logger.debug("Inicializando Playwright")
            try:
                playwright = await async_playwright().start()
                logger.debug("Abrindo navegador Chromium")
                browser = await playwright.chromium.launch(headless=self.headless)
                logger.debug("Modo headless: %s", self.headless)

                page = await browser.new_page()

                logger.debug("Navegando para %s", self._base_url)
                await page.goto(self._base_url, wait_until="load")
                return playwright, browser, page
            except Exception:
                logger.exception(
                    "Falha ao iniciar o navegador do Playwright. "
                    "Certifique-se de que os browsers estao instalados com 'playwright install'."
                )
                raise

        self._playwright, browser, page = await _launch()
        self._browser = browser
        self._page = page
        return self._browser, self._page

    async def collect_information_popup(
        self, timeout: int = 3000
    ) -> dict[str, list[str]]:
        """
        Coleta todos os informes da popup, estruturando como {data: [linhas de texto, ...]}, e fecha a popup.

        Retorno
        -------
        dict
            Dicionário {data: [lista de linhas de conteúdo]}
        """
        if not self._page:
            await self.startup()

        context = self._page.context
        popup = None
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) * 1000 < timeout:
            for current_page in context.pages:
                if (
                    current_page != self._page
                    and "popupMensagensInformativas.jsf" in current_page.url
                ):
                    popup = current_page
                    break
            if popup:
                break
            await asyncio.sleep(0.1)
        if not popup:
            logger.debug("Nenhuma popup de informacoes encontrada")
            return {}

        logger.debug("Coletando mensagens da popup de informacoes")

        await popup.wait_for_load_state("domcontentloaded")

        trs = popup.locator("table#listaMensagens tr.rich-table-row")
        count = await trs.count()

        for i in range(count):
            tr = trs.nth(i)
            date_elem = tr.locator('p[align="center"] > b > span')
            if await date_elem.count() == 0:
                continue
            notice_date = (await date_elem.first.inner_text()).strip()

            subject_elem = tr.locator("p").nth(1)
            notice_subject = (await subject_elem.inner_text()).strip()

            lines = []
            ps = tr.locator("div#divDesc p")
            ps_count = await ps.count()
            for j in range(ps_count):
                texto = (await ps.nth(j).inner_text()).strip()
                if texto:
                    lines.append(texto)
            self._information_messages[(notice_date, notice_subject)] = lines

        await popup.close()

        return self._information_messages
