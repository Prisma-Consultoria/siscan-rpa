from enum import Enum
from typing import Optional
import time
import logging
from playwright.sync_api import Page, Locator, TimeoutError, ElementHandle
from src.siscan.context import SiscanBrowserContext
from src.siscan.exception import SiscanMenuNotFoundError, \
    XpathNotFoundError, SiscanException

logger = logging.getLogger(__name__)


class InputType(Enum):
    """
    # Exemplo de uso
    tipo = LogicalInputType.CHECKBOX
    print(tipo.html_element)  # 'input'
    """
    TEXT = "text"
    DATE = "date"
    VALUE = "value"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    LIST = "list"
    SELECT = "select"
    RADIO = "radio"

    @property
    def html_element(self) -> str:
        if self in {
            InputType.TEXT,
            InputType.DATE,
            InputType.VALUE,
            InputType.NUMBER,
            InputType.CHECKBOX,
        }:
            return "input"
        elif self == InputType.TEXTAREA:
            return "textarea"
        elif self in {InputType.LIST, InputType.SELECT}:
            return "select"
        elif self == InputType.RADIO:
            return "radio"
        else:
            raise ValueError(f"Tipo de input não suportado: {self.value}")


DEFAULT_TIMEOUT = 5


class XPathConstructor:
    DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
    # Fator de conversão de segundos para milissegundos
    TIMEOUT_MS_FACTOR = 1000
    # Intervalo entre tentativas de repetição (em segundos)
    ELAPSED_INTERVAL = 0.2  # segundos

    """
    Construtor de XPaths reutilizáveis para localizar elementos na página.
    Compatível com Playwright (não usa Selenium).
    """
    def __init__(self, context: SiscanBrowserContext, xpath=''):
        self._page = context.page
        self._browser = context.browser
        self._context = context
        self._xpath = xpath

        self._input_type: Optional[str] = None

    def __str__(self):
        return (f"XPathConstructor(xpath='{self._xpath}', "
                f"input_type='{self._input_type}')")

    def _get_input_type(
            self, default_input_type: str | InputType = None) -> InputType:
        """
        Obtém o tipo de input como Enum InputType a partir de string ou já
        do próprio Enum.
        """
        if isinstance(default_input_type, InputType):
            return default_input_type

        if default_input_type is None:
            input_type = self._input_type or InputType.TEXT
        else:
            input_type = default_input_type

        if isinstance(input_type, InputType):
            return input_type
        try:
            return InputType[input_type.upper()]
        except KeyError:
            raise ValueError(f"Tipo de input desconhecido: {input_type.html_element}")

    @property
    def page(self) -> Page:
        return self._page

    @property
    def browser(self):
        return self._browser

    @property
    def context(self):
        return self._context

    @property
    def xpath(self):
        return self._xpath

    def reset(self):
        self._xpath = ''
        self._input_type = None

    def exists(self, timeout: float = DEFAULT_TIMEOUT) -> bool:
        """
        Verifica se o elemento identificado pelo XPath corrente existe no DOM.
        Não lança exceção se não encontrar o elemento, apenas retorna False.

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo, em segundos, para aguardar a presença do elemento.

        Retorno
        -------
        exists : bool
            True se o elemento existe, False caso contrário.
        """
        try:
            locator = self.page.locator(f'xpath={self._xpath}')
            # Aguarda até timeout, pode ser útil em campos dinâmicos
            locator.wait_for(
                state="attached",
                timeout=timeout * self.TIMEOUT_MS_FACTOR)
            return locator.count() > 0
        except Exception:
            return False

    def get(self) -> Page.locator:
        """
        Retorna um locator Playwright baseado no XPath corrente da instância.

        Este método é responsável por criar e retornar um locator do Playwright
        utilizando o XPath armazenado em `self._xpath`. O locator é o objeto
        preferencial para interações com elementos na página, conforme
        recomendado pela documentação oficial do Playwright.

        Caso o elemento não seja encontrado (count == 0), dispara uma exceção
        personalizada `XpathNotFoundError`, incluindo o contexto atual e o
        XPath buscado.

        Em caso de erro inesperado durante a obtenção do locator, a exceção
        original é registrada no log e, em seguida, encapsulada e lançada como
        `XpathNotFoundError`.

        Retorno
        -------
        elem : Locator
            Instância de locator correspondente ao XPath corrente.

        Exceções
        --------
        XpathNotFoundError
            Disparada quando o XPath não encontra nenhum elemento
            correspondente na página ou ocorre erro inesperado durante o
            processo.

        Exemplos
        --------
        ```python
        xpath = XPathConstructor(page)
        locator = xpath.find_form_input("Nome:").get()
        locator.fill("Maria")
        ```

        Notas
        -----
        Este método é utilizado internamente por outras funções de interação
        como `wait_and_get`, `fill`, `click`, entre outros.

        """
        # Recomendada pelo Playwright.
        # Locator é a forma preferida de interagir com elementos
        try:
            if self.exists(timeout=DEFAULT_TIMEOUT):
                logger.debug(f"Obtendo locator com XPath: {self._xpath}")
                elem = self.page.locator(f'xpath={self._xpath}')
                if elem.count() == 0:
                    raise XpathNotFoundError(self._context, xpath=self._xpath)
                return elem
        except Exception as e:
            logger.error(f"Erro inesperado ao obter locator com "
                         f"XPath '{self._xpath}': {e}")
            # Envolve a exceção original na nossa exceção específica
            raise XpathNotFoundError(
                self._context,
                xpath=self._xpath,
                msg=f"Erro inesperado ao obter locator: {e}"
            )
            raise

    def wait_and_get(self, timeout: float = DEFAULT_TIMEOUT) -> Page.locator:
        """
        Aguarda até que o elemento identificado pelo XPath esteja visível e
        retorna o Locator correspondente.

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo de espera, em segundos. O padrão é 10 segundos.

        Retorno
        -------
        locator : Locator
            Instância Playwright Locator do elemento encontrado.

        Exceções
        --------
        XpathNotFoundError
            Disparada caso o elemento não fique visível no tempo estipulado.

        Exemplo
        -------
        ```python
        locator = xpath.wait_and_get(timeout=15)
        ```
        """
        locator = self.get()
        logger.debug(f"Aguardando elemento com XPath: {self._xpath} "
                     f"por {timeout * self.TIMEOUT_MS_FACTOR} milessegundos.")
        try:
            locator.wait_for(state="visible",
                             timeout=timeout * self.TIMEOUT_MS_FACTOR)
            return locator
        except TimeoutError:
            # Se o wait_for estourar timeout, o elemento não se tornou visível
            logger.error(f"Timeout: Elemento com XPath '{self._xpath}' "
                         f"não se tornou visível em "
                         f"{timeout * self.TIMEOUT_MS_FACTOR} milessegundos.")
            raise XpathNotFoundError(
                self._context,
                xpath=self._xpath,
                msg=f"Elemento não visível: XPath '{self._xpath}' "
                    f"não se tornou visível dentro do tempo limite."
            )
        except XpathNotFoundError:
            # Se o .get() já lançou essa exceção, apenas relança
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao aguardar e obter locator com "
                         f"XPath '{self._xpath}': {e}")
            raise XpathNotFoundError(
                self._context,
                xpath=self._xpath,
                msg=f"Erro inesperado ao aguardar elemento: {e}"
            )
        return locator

    def wait_until_enabled(self, locator: Locator = None,
                           timeout: float = DEFAULT_TIMEOUT):
        """
        Aguarda até que o campo identificado pelo XPath atual esteja
        habilitado.

        Este método espera que o elemento correspondente ao XPath não possua o
        atributo 'disabled', ou seja, esteja disponível para interação.

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo de espera, em segundos. O padrão é 10 segundos.

        Retorno
        -------
        self : XPathConstructor
            Permite o encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath.wait_until_enabled(timeout=15)
        ```
        """
        locator = locator or self.get()
        elapsed = 0
        interval = 0.2
        while elapsed < timeout:
            try:
                # Se não existe ou está invisível, ignore erro
                if locator.count() == 0:
                    time.sleep(interval)
                    elapsed += interval
                    continue
                # Verifica atributo disabled
                if locator.is_visible() and locator.is_enabled():
                    logger.debug(f"Elemento enable, xpath: {self.xpath}")
                    return self
            except Exception:
                pass
            time.sleep(interval)
            elapsed += interval
        raise TimeoutError("Elemento não ficou habilitado a tempo")

    def wait_until_filled(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Aguarda até que o campo localizado pelo XPath atual seja preenchido
        (não vazio).

        Este método utiliza dois estágios de verificação:
        1. Aguarda até o elemento identificado pelo XPath esteja visível
           na página.
        2. Aguarda até que o atributo 'value' do elemento possua algum
           conteúdo (isto é, o campo foi preenchido, seja por usuário,
           script ou autofill).

        Caso o elemento não se torne visível ou não seja preenchido dentro
        do tempo limite especificado, uma exceção `XpathNotFoundError` será
        disparada, contendo detalhes do contexto e do XPath utilizado.

        Parâmetros
        ----------
        timeout : int, opcional (default=10)
            Tempo máximo, em segundos, para aguardar o preenchimento do campo.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir encadeamento de métodos.

        Exceções
        --------
        XpathNotFoundError
            Disparada quando o campo não é localizado, não se torna visível ou
            não é preenchido no tempo especificado.

        Exemplos
        --------
        ```python
        xpath = XPathConstructor(page)
        xpath.find_form_input("Nome:").wait_until_filled(timeout=15)
        nome = xpath.get_value()
        ```

        Notas
        -----
        - Utiliza o fator multiplicativo TIMEOUT_MS_FACTOR para converter
          segundos em milissegundos conforme requerido pelo Playwright.
        - O método encapsula falhas de localização e preenchimento, gerando
          logs de erro detalhados e relançando exceções personalizadas para
          rastreamento mais eficaz.

        """
        try:
            # Obtém o locator Playwright a partir do XPath corrente
            # Isso pode levantar SiscanElementNotFoundError se o locator não
            # for encontrado
            locator = self.get()

            # Primeiro, espera até o elemento estar visível
            logger.debug(f"Aguardando preenchimento do campo localizado por "
                         f"XPath: {self._xpath}")
            locator.wait_for(state="visible",
                             timeout=timeout * (self.TIMEOUT_MS_FACTOR/2)
                             )

            # Em seguida, espera até o atributo 'value' ser diferente de vazio
            logger.debug(
                f"Esperando o campo com XPath '{self._xpath}' "
                f"ter valor preenchido.")
            self.page.wait_for_function(
                """(element) => {
                    return element.value.length > 0;
                }""",
                arg=locator.element_handle(),
                timeout=timeout * (self.TIMEOUT_MS_FACTOR/2)
            )
            logger.info(
                f"Campo com XPath '{self._xpath}' foi preenchido com sucesso.")
            return self
        except TimeoutError as e:
            # Captura timeouts do wait_for(state="visible")
            # ou wait_for_function
            logger.error(f"Timeout: O campo '{self._xpath}' não foi "
                         f"preenchido ou não se tornou visível dentro "
                         f"de {timeout * self.TIMEOUT_MS_FACTOR} "
                         f"milessegundos. Erro: {e}")
            raise XpathNotFoundError(
                self._context,
                xpath=self._xpath,
                msg=f"Campo não preenchido ou visível: XPath '{self._xpath}' "
                    f"não atendeu às condições dentro do tempo limite."
            )
        except XpathNotFoundError:
            # Se a exceção já veio do self.get(), apenas a relançamos
            raise
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas durante o processo
            logger.error(f"Erro inesperado ao aguardar o preenchimento do "
                         f"campo com XPath '{self._xpath}': {e}")
            raise XpathNotFoundError(
                self._context,
                xpath=self._xpath,
                msg=f"Erro inesperado ao aguardar o preenchimento: {e}"
            )

    def wait_page_ready(
            self, timeout: float = DEFAULT_TIMEOUT) -> 'XPathConstructor':
        """
        Aguarda até que a página esteja completamente carregada e o jQuery
        (se usado) esteja disponível.

        Este método espera pelo estado 'networkidle', indicando que não
        há mais requisições de rede em andamento, e garante que o jQuery
        já foi carregado e está acessível na página.

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo de espera, em segundos. O padrão é 10 segundos.

        Retorno
        -------
        self : XPathConstructor
            Permite o encadeamento de métodos.

        Exceções
        --------
        SiscanException
            Se a página não carregar completamente ou o jQuery não estiver
            disponível dentro do tempo limite.
        """
        try:
            logger.debug(f"Aguardando o estado 'networkidle' da página. "
                         f"Timeout: {timeout * self.TIMEOUT_MS_FACTOR} "
                         f"milessegundos.")
            self.page.wait_for_load_state(
                "networkidle", timeout=timeout * self.TIMEOUT_MS_FACTOR)
            logger.debug("Estado 'networkidle' alcançado.")

            # Espera pelo jQuery, caso a aplicação o utilize.
            # Esta verificação é opcional; remova-a se sua aplicação não usa
            # jQuery.
            logger.debug(f"Verificando a disponibilidade do jQuery na página. "
                         f"Timeout: {timeout * self.TIMEOUT_MS_FACTOR} "
                         f"milessegundos.")
            self.page.wait_for_function(
                "window.jQuery !== undefined "
                "&& typeof jQuery === 'function'",
                timeout=timeout * self.TIMEOUT_MS_FACTOR
            )
            logger.info("Página pronta e jQuery disponível.")
            return self

        except TimeoutError as e:
            # Captura timeouts do wait_for_load_state ou wait_for_function
            logger.error(f"Timeout: A página não ficou pronta ou o jQuery não "
                         f"carregou dentro de . Erro: {e}")
            raise SiscanException(
                self._context,
                msg=f"Página não carregada ou jQuery indisponível dentro do "
                    f"tempo limite: {e}"
            )
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas
            logger.error(f"Erro inesperado ao aguardar a prontidão da "
                         f"página: {e}")
            raise SiscanException(
                self._context,
                msg=f"Erro inesperado ao aguardar a prontidão da página: {e}"
            )

    def get_value(
            self, input_type: str | InputType = None,
            timeout: float = DEFAULT_TIMEOUT
    ) -> tuple[str, str] | list[tuple[str, str]]:
        """
        Obtém o valor de um campo localizado via XPath, retornando sempre uma
        tupla `(texto, valor)` conforme o tipo do campo.

        O método adapta a extração do valor conforme o tipo do campo:
          - Para campos de texto (`text`, `textarea`), retorna uma tupla
            contendo o valor digitado duas vezes: `(valor, valor)`.
          - Para campos select, retorna `(texto_opcao_selecionada,
            value_opcao_selecionada)`.
          - Para checkbox:
              - Se houver apenas um checkbox, retorna `(texto_associado,
                value)` se estiver marcado, ou `(None, None)` se não estiver.
              - Se houver múltiplos checkboxes, retorna uma lista de tuplas
                para os checkboxes marcados: `[(texto, value), ...]`.
          - Para radio, retorna `(texto_associado, value)` para o radio
            selecionado, ou `(None, None)` se nenhum estiver marcado.
          - Para elementos do tipo div ou span, retorna o texto como
            `(texto, texto)`.
          - Para outros tipos, retorna `(valor, valor)`.

        Parâmetros
        ----------
        type_input : str, opcional
            Tipo do campo a ser lido ('text', 'select', 'checkbox', 'radio',
            'multiple-checkbox', 'div', 'span', etc.). O padrão é 'text'.
        timeout : int, opcional
            Tempo máximo (em milissegundos) para aguardar o elemento.
            Padrão: 500.

        Retorno
        -------
        tuple[str, str] | list[tuple[str, str]]
            Tupla (texto, valor) correspondente ao campo, ou lista de tuplas
            no caso de múltiplos checkboxes.
            Retorna (None, None) quando o campo não está preenchido ou nenhum
            item está marcado/selecionado.

        Exemplo
        -------
        ```
        texto, valor = xpath.get_value(InputType.SELECT)
        print(texto, valor)  # ex: 'Feminino', 'F'
        lista = xpath.get_value(InputType.CHECKBOX)  # Se múltiplos checkboxes marcados
        print(lista)  # [('Opção 1', '1'), ('Opção 2', '2')]
        texto, valor = xpath.get_value(InputType.RADIO)
        texto, valor = xpath.get_value(InputType.TEXT)
        ```
        """
        locator = self.wait_and_get(timeout)
        input_type = self._get_input_type(input_type)

        if input_type in (InputType.TEXT, InputType.TEXTAREA):
            value = locator.input_value()
            return (value, value)
        elif input_type == InputType.SELECT:
            # Retorna o texto visível da opção selecionada
            selected_option = locator.locator('option:checked')
            value = selected_option.get_attribute("value")
            text = selected_option.inner_text().strip()
            return (text, value)
        elif input_type == InputType.CHECKBOX:
            # Checa quantos checkboxes existem
            checkboxes = locator.locator("input[type='checkbox']")
            count = checkboxes.count()
            # Um único checkbox count = 1
            # Múltiplos checkboxes count > 1
            result = []
            for i in range(count):
                text = None
                cb = checkboxes.nth(i)
                if cb.is_checked():
                    value = cb.get_attribute("value")
                    checkbox_id = cb.get_attribute("id")
                    if checkbox_id:
                        # Busca o label associado ao id
                        label_elem = locator.page.locator(
                            f"label[for='{checkbox_id}']")
                        if label_elem.count() > 0:
                            text = label_elem.nth(0).inner_text().strip()
                    if not text:
                        label_elem = cb.evaluate_handle("node => node.closest('label')")
                        if label_elem and isinstance(label_elem, ElementHandle):
                            text = label_elem.inner_text().strip()
                        else:
                            text = value
                    result.append((text, value))
                return result
            else:
                return (None, None)
        elif input_type == InputType.RADIO:
            # Retorna o value do radio marcado, ou None se nenhum marcado
            radios = locator.locator("input[type='radio']")
            count = radios.count()
            for i in range(count):
                text = None
                radio = radios.nth(i)
                if radio.is_checked():
                    value = radio.get_attribute("value")
                    radio_id = radio.get_attribute("id")
                    if radio_id:
                        # Busca o label associado ao id
                        label_elem = locator.page.locator(
                            f"label[for='{radio_id}']")
                        if label_elem.count() > 0:
                            text = label_elem.nth(0).inner_text().strip()
                    if not text:
                        label_elem = radio.evaluate_handle(
                            "node => node.closest('label')")
                        if label_elem and isinstance(label_elem, ElementHandle):
                            text = label_elem.inner_text().strip()
                        else:
                            text = value
                    return (text, value)
            return (None, None)
        elif input_type in ("div", "span"):
            text = locator.inner_text().strip()
            return (text, text)
        else:
            value = locator.input_value()  # Padrão
            return (value, value)

    def _select_option_with_retry(
            self, obj_locator, value: str, timeout: float = DEFAULT_TIMEOUT,
            interval: float = None):
        """
        Realiza a seleção de uma opção em um campo <select>, com tentativas
        repetidas até que a opção desejada esteja disponível ou até que o tempo
        limite seja atingido.

        O método itera sobre as opções do elemento <select> identificado por
        `obj_locator`, buscando uma opção cujo atributo 'value' seja igual ao
        valor informado em `value`. Caso não encontre imediatamente, o método
        repete a verificação a cada intervalo definido por `interval`, até o
        tempo máximo especificado por `timeout`. Caso o valor informado seja
        `None`, o método apenas emite um aviso no logger e retorna sem realizar
        qualquer seleção.

        Parâmetros
        ----------
        obj_locator : Locator
            Objeto Locator do Playwright apontando para o elemento <select>.
        value : str
            Valor do atributo 'value' da opção que se deseja selecionar.
        timeout : int, opcional
            Tempo máximo de espera, em segundos, até localizar e selecionar a
            opção desejada. O padrão é 10 segundos.
        interval : float, opcional
            Intervalo, em segundos, entre tentativas de verificação. Se não
            informado, utiliza o valor padrão de `self.RETRY_INTERVAL`.

        Exceções
        --------
        TimeoutError
            Disparada caso a opção desejada não seja localizada dentro do tempo
            limite especificado.

        Notas
        -----
        Este método é útil para cenários onde as opções do select podem ser
        carregadas de forma assíncrona (exemplo: via AJAX), garantindo robustez
        diante de atrasos ou variações do front-end.

        Exemplo
        -------
        ```
        self._select_option_with_retry(select_locator, "5", timeout=15)
        ```
        """
        interval = interval or self.ELAPSED_INTERVAL
        if value == 'None' or value is None:
            logger.warning(
                "Valor vazio para campo do tipo 'select'. "
                "Nenhum valor será selecionado.")
            return

        elapsed = 0
        while elapsed < timeout:
            options = obj_locator.locator("option")
            count = options.count()
            found = False
            for i in range(count):
                opt_value = options.nth(i).get_attribute("value")
                if opt_value == value:
                    found = True
                    break
            if found:
                obj_locator.select_option(value=value)
                return
            time.sleep(interval)
            elapsed += interval

        raise TimeoutError(
            f"Timeout ao selecionar opção '{value}' no <select>: "
            "opção não encontrada após aguardar carregamento."
        )

    def _select_radio_with_retry(
            self,
            obj_locator: "Locator",
            value: str,
            timeout: float = TIMEOUT_MS_FACTOR,
            interval: float = None
    ) -> None:
        """
        Realiza a seleção de um radio button cujo value seja igual ao valor
        fornecido, repetindo as tentativas até que o radio esteja disponível,
        habilitado e selecionável.

        Parâmetros
        ----------
        obj_locator : Locator
            Objeto Locator do Playwright apontando para o grupo de radio
            buttons.
        value : str
            Valor do atributo 'value' do radio que se deseja selecionar.
        timeout : float, opcional
            Tempo máximo de espera, em segundos, até localizar e selecionar o
            radio desejado. Padrão: 10 segundos.
        interval : float, opcional
            Intervalo, em segundos, entre tentativas. Padrão: 0.2 segundos.

        Exceções
        --------
        TimeoutError
            Disparada caso o radio button desejado não seja localizado ou
            selecionado dentro do tempo limite.
        """
        interval = interval or self.ELAPSED_INTERVAL
        elapsed = 0
        while elapsed < timeout:
            radios = obj_locator.locator("input[type='radio']")
            count = radios.count()
            found = False

            for i in range(count):
                radio = radios.nth(i)
                radio_value = radio.get_attribute("value")
                is_checked = radio.is_checked()
                is_disabled = radio.get_attribute("disabled")
                if radio_value == value:
                    found = True
                    if not is_checked and not is_disabled:
                        try:
                            radio.check(force=True)
                            logger.debug(
                                f"Radio value={value} selecionado com "
                                f"sucesso.")
                            return
                        except Exception as e:
                            logger.warning(
                                f"Falha ao selecionar radio "
                                f"value={value}: {e}")
                            # Pode ser overlay, atraso do frontend, etc.
                    elif is_checked:
                        logger.debug(
                            f"Radio value={value} já estava selecionado.")
                        return
                    # Se está desabilitado, aguarda
            if found:
                # Radio localizado mas não foi possível selecionar, espera e
                # tenta de novo
                time.sleep(interval)
                elapsed += interval
            else:
                # Radio ainda não apareceu, espera e tenta de novo
                time.sleep(interval)
                elapsed += interval
        raise TimeoutError(
            f"Timeout ao tentar selecionar o radio com value='{value}'."
        )

    def find_search_link_after_input(
            self, label_name: str) -> 'XPathConstructor':
        """
        Localiza o link (<a>) de busca (ex: ícone de lupa) imediatamente após
        um campo input identificado pelo label.

        Este método utiliza a lógica de find_form_input para identificar o
        campo input relacionado ao label informado, em seguida monta o XPath
        para selecionar o elemento <a> subsequente ao campo input.

        Parâmetros
        ----------
        label_name : str
            Texto do label associado ao campo input desejado.

        Retorno
        -------
        self : XPathConstructor
            Permite o encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath.find_search_link_after_input("Cartão SUS").click()
        ```
        """
        # Reaproveita a lógica de find_form_input para montar o XPath até o
        # campo input
        self.find_form_input(label_name, input_type=InputType.TEXT)
        # Adiciona o seletor para o <a> logo após o campo
        self._xpath += "/following-sibling::a[1]"
        logger.debug(f"XPath para lupa após input "
                     f"'{label_name}': {self._xpath}")
        return self

    def find_form_input(
            self, label_name: str, input_type: str | InputType = None
    ) -> 'XPathConstructor':
        """
        Localiza um campo de formulário (input, select, textarea, date,
        checkbox ou radio) associado a um label específico, construindo
        dinamicamente o XPath apropriado para o tipo de campo informado.

        O método implementa diferentes estratégias de localização, de acordo
        com o tipo do campo:
          - Para 'date', busca o input do calendário dentro do span subsequente
            ao label.
          - Para 'checkbox', localiza a tabela imediatamente após o label.
          - Para 'radio', procura pelo fieldset cujo legend corresponda ao
            texto do label.
          - Para 'select', utiliza o atributo 'for' do label para mapear o
            select pelo id. Caso não exista, tenta localizar o select como
            irmão direto ou descendente do mesmo ancestral.
          - Para outros tipos (ex: 'text', 'textarea'), assume o campo como
            irmão direto do label.

        Parâmetros
        ----------
        label_name : str
            Texto do label do campo a ser localizado (deve estar exatamente
            como exibido na interface, incluindo pontuação, se houver).
        type_input : str, opcional
            Tipo do campo a ser localizado: 'text', 'select', 'textarea',
            'date', 'checkbox' ou 'radio'. Padrão: 'text'.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir o encadeamento de
            métodos.

        Exceções
        --------
        XpathNotFoundError
            Disparada se o label informado não for encontrado na página.
        Exception
            Disparada se, no caso de campos do tipo 'select', não for possível
            localizar o elemento <select> associado ao label, após todas as
            tentativas.

        Exemplos
        --------
        ```
        xpath.find_form_input("Unidade de Saúde", InputType.SELECT)
        xpath.find_form_input("Data de Nascimento", InputType.DATE)
        xpath.find_form_input("Sexo", InputType.CHECKBOX)
        ```

        Notas
        -----
        Este método é tolerante a diferentes estruturas de HTML frequentemente
        encontradas em sistemas legados e sistemas web governamentais, lidando
        com cenários onde o relacionamento label-campo não segue padrões W3C.
        """
        input_type = self._get_input_type(input_type)
        label_xpath = f"//label[normalize-space(text())='{label_name}']"

        if input_type == InputType.DATE:
            # Para campos de data, encontra o span após o label e dentro dele
            # busca o input de texto do calendário
            self._xpath += (
                f"{label_xpath}/following-sibling::span[1]//{input_type.html_element}"
                f"[contains(@class, 'date') or contains(@class, 'calendar')]"
            )
        elif input_type == InputType.CHECKBOX:
            # Para checkbox, busca todos os inputs do tipo checkbox após o
            # label, dentro de qualquer estrutura (ex: tabela)
            self._xpath += (
                f"{label_xpath}/following-sibling::table[1]"
                f"|//fieldset[legend[normalize-space(text())='{label_name}']]"
            )
        elif input_type == InputType.RADIO:
            # Para radio: busca no fieldset com legend igual ao label_name
            self._xpath += (
                f"//fieldset[legend[normalize-space(text())='{label_name}']]"
                f"|//fieldset[legend[contains(normalize-space(.), '{label_name}')]]"
            )
        elif input_type == InputType.SELECT:
            # Busca primeiro por 'for'
            label_elem = self.page.locator(label_xpath)
            if label_elem.count() == 0:
                logger.debug(
                    f"Label '{label_name}' não encontrado com "
                    f"XPath {label_xpath}")
                raise XpathNotFoundError(self._context, xpath=label_xpath)
            select_id = label_elem.first.get_attribute("for")
            if select_id:
                # Caminho padrão: label->for->select#id
                self._xpath = f"//select[@id='{select_id}']"
            else:
                # Caminho alternativo: select irmão
                self._xpath = f"{label_xpath}/following-sibling::select[1]"
                # Opcional: checar se existe, caso contrário, tente por
                # ancestral comum
                if self.page.locator(self._xpath).count() == 0:
                    # Busca por select descendente do mesmo div ancestral
                    self._xpath = (
                        f"{label_xpath}/ancestor::div[1]//select[1]"
                    )
        else:
            # Para outros tipos, mantém o comportamento padrão (irmão direto)
            self._xpath += (
                f"{label_xpath}/following-sibling::{input_type.html_element}[1]"
            )
        self._input_type = input_type
        logger.debug(f"XPath: {self}")
        return self

    def fill(self, value: str, input_type: str | InputType = None,
             timeout: float = DEFAULT_TIMEOUT,
             reset=True) -> 'XPathConstructor':
        """
        Preenche campos de formulário de diferentes tipos (input, select,
        checkbox, radio, lista), de acordo com o tipo especificado, utilizando
        abordagens específicas para cada estrutura de campo.

        O método identifica o tipo do campo e executa o preenchimento conforme
        o padrão do elemento:
          - Para 'select' ou 'lista', seleciona a opção cujo value seja igual
            ao valor fornecido, com mecanismo de retry.
          - Para 'checkbox', marca ou desmarca os checkboxes necessários para
            refletir os valores informados.
          - Para 'radio', seleciona o botão de rádio do grupo correspondente ao
            valor.
          - Para outros tipos (ex: texto, textarea), preenche o campo via
            método fill do Playwright.

        Parâmetros
        ----------
        value : str
            Valor a ser preenchido no campo (ou lista de valores para
            checkboxes).
        type_input : str, opcional
            Tipo do campo ('texto', 'select', 'checkbox', 'radio', 'lista').
            O padrão é 'texto'.
        timeout : int, opcional
            Tempo máximo para aguardar o campo estar disponível, em segundos.
            O padrão é 10 segundos.
        reset : bool, opcional
            Se True, reseta o XPath interno após o preenchimento.
            Default: True.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir encadeamento de métodos.

        Exceções
        --------
        TimeoutError
            Disparada se o campo não puder ser localizado ou preenchido no
            tempo limite.
        Warning
            Um aviso é registrado no logger se o valor não for encontrado para
            radio ou select, ou se o valor for vazio para select/lista.

        Exemplos
        --------
        ```
        xpath.find_form_input("Sexo", InputType.CHECKBOX).fill("M")
        xpath.find_form_input("Escolaridade", InputType.SELECT).fill("4")
        xpath.find_form_input("Tipo de Exame", InputType.RADIO).fill("03")
        ```

        Notas
        -----
        O método é tolerante a campos dinâmicos ou carregamentos parciais,
        realizando tentativas com retry para selects/listas. Campos do tipo
        'checkbox' aceitam múltiplos valores (como lista).
        """
        # if value is None:
        #     raise ValueError("value não pode ser nulo.")

        input_type = self._get_input_type(input_type)

        locator = self.wait_and_get(timeout)
        logger.debug(
            f"Preenchendo o campo do tipo {input_type.html_element} com "
            f"valor: {value}"
        )
        if input_type in (InputType.SELECT, InputType.SELECT):
            if value is None:
                logger.warning(
                    f"Valor vazio para campo do tipo {input_type.html_element}"
                    ". Nenhum valor será preenchido.")
                return self
            self._select_option_with_retry(locator, value, timeout)
        elif input_type == InputType.CHECKBOX:
            # Para checkbox: encontrar todos os inputs dentro da tabela
            # localizada
            valores = value if isinstance(value, list) else [value]
            # Usar CSS selector!
            checkboxes = locator.locator("input[type='checkbox']")
            count = checkboxes.count()
            for i in range(count):
                input_el = checkboxes.nth(i)
                input_value = input_el.get_attribute("value")
                is_checked = input_el.is_checked()
                if input_value in valores and not is_checked:
                    logger.debug(f"Marcando checkbox value={input_value} "
                                 f"(checked={is_checked})")
                    input_el.check(force=True)
                elif input_value not in valores and is_checked:
                    logger.debug(f"Desmarcando checkbox value={input_value} "
                                 f"(checked={is_checked})")
                    input_el.uncheck(force=True)
        elif input_type == InputType.RADIO:
            self._select_radio_with_retry(locator, value, timeout)
        else:
            locator.fill(value, force=True)
        if reset:
            self.reset()
        return self

    def find_form_button(self, button_text: str) -> 'XPathConstructor':
        """
        Localiza um botão de formulário pelo texto apresentado ao usuário.

        Este método constrói um XPath capaz de localizar, em ordem de
        prioridade:
            - Um elemento <input> do tipo 'submit' cujo atributo 'value'
              corresponda exatamente ao texto informado;
            - Um elemento <button> cujo texto interno corresponda exatamente
              ao texto informado;
            - Um elemento <a> com classe 'form-button' e cujo texto interno
              corresponda exatamente ao texto informado.

        Parâmetros
        ----------
        button_text : str
            Texto exibido no botão do formulário, conforme apresentado na
            interface.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir o encadeamento de
            métodos.

        Exemplo
        -------
        ```python
        xpath = XPathConstructor(page)
        xpath.find_form_button("Pesquisar").click()
        ```

        Observações
        -----------
        - A busca é sensível a maiúsculas/minúsculas e a espaços em branco.
        - Recomenda-se informar o texto exatamente como apresentado na
          interface.
        """
        self._xpath = (
            f"(//input[@type='submit' "
            f"and normalize-space(@value)='{button_text}']"
            f"|//button[normalize-space(string(.))='{button_text}']"
            f"|//a[contains(@class,'form-button') "
            f"and normalize-space(string(.))='{button_text}'])[1]"
        )
        logger.debug(f"XPath do botão localizado: {self}")
        return self

    def find_form_anchor_button(
            self, button_text: str) -> 'XPathConstructor':
        """
        Localiza um botão de formulário do tipo <a> (âncora) com classe
        'form-button' e texto especificado.

        Este método constrói um XPath para selecionar o elemento <a> que possua
         a classe 'form-button' e cujo texto exibido seja exatamente igual ao
        valor de `button_text`, ignorando espaços extras.

        Parâmetros
        ----------
        button_text : str
            Texto exibido no botão âncora, conforme apresentado na interface
            do formulário.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath = XPathConstructor(page)
        xpath.find_form_anchor_button("Pesquisar").click()
        ```
        """
        # O XPath localiza <a> com classe form-button e texto igual ao
        # informado (ignorando espaços extras)
        self._xpath = (
            f"(//a[contains(concat(' ', normalize-space(@class), ' ')"
            f", ' form-button ') "
            f"and normalize-space(text())='{button_text}'])[1]"
        )
        logger.debug(f"XPath do botão <a> localizado: {self._xpath}")
        return self

    def click(self,
              timeout: float = DEFAULT_TIMEOUT,
              interval: float = None,
              wait_for_selector: str = None, reset=True) -> 'XPathConstructor':
        """
        Realiza o clique forçado no elemento localizado pelo XPath corrente,
        repetindo tentativas até sucesso ou atingir o tempo limite. Se
        `wait_for_selector` for fornecido, o método também aguardará a
        presença desse seletor após o clique.

        Este método é resiliente a delays ou instabilidades do front-end,
        tentando clicar no elemento repetidas vezes até que o clique seja
        bem-sucedido ou o tempo máximo seja atingido. O clique é realizado em
        modo "force", o que permite interagir com elementos que possam estar
        temporariamente cobertos ou sobrepostos por outros componentes da
        interface.

        Parâmetros
        ----------
        timeout : int, opcional (default=10)
            Tempo máximo, em segundos, para tentar o clique até considerar
            falha.
        interval : float, opcional (default=self.RETRY_INTERVAL)
            Intervalo, em segundos, entre cada tentativa de clique.
        reset : bool, opcional (default=True)
            Se True, reseta o XPath interno após o clique bem-sucedido.
        wait_for_selector : str, opcional (default=None)
            Se definido, após o clique o método aguardará até o seletor CSS ou
            XPath informado estar presente e visível.

        Retorno
        -------
        self : XPathConstructor
            Permite encadeamento de métodos.

        Exceções
        --------
        TimeoutError
            Disparada se o clique não puder ser realizado dentro do tempo
            limite especificado, ou se o seletor esperado não aparecer.

        Exemplos
        --------
        ```python
        xpath.find_form_button("Pesquisar").click(
        ...     wait_for_selector="table#frm\\:listaPaciente"
        ... )
        xpath.find_form_input("Nome:").click(timeout=5)
        ```

        Notas
        -----
        O clique é executado com 'force=True' do Playwright, permitindo ação
        mesmo em elementos não interativos no momento. Recomenda-se utilizar
        este método quando a interface apresentar delays frequentes ou overlays
        transitórios.
        """
        interval = interval or self.ELAPSED_INTERVAL

        elapsed = 0
        while elapsed < timeout:
            try:
                locator = self.wait_and_get(timeout)
                logger.debug(f"Clicando no elemento localizado com XPath: "
                             f"{self._xpath}")
                locator.click(force=True)
                if wait_for_selector:
                    logger.debug(f"Aguardando seletor após clique: "
                                 f"{wait_for_selector}")
                    self.page.wait_for_selector(
                        wait_for_selector, state="visible",
                        timeout=timeout * self.TIMEOUT_MS_FACTOR
                    )
                if reset:
                    self.reset()
                return self
            except Exception as e:
                time.sleep(interval)
                elapsed += interval
        raise TimeoutError(f'Timeout ao clicar no elemento {self.xpath} após '
                           f'{timeout * self.TIMEOUT_MS_FACTOR} '
                           f'milessegundos.')

    def click_menu_action(self, menu_name: str, menu_action_text: str,
                          timeout: float = DEFAULT_TIMEOUT,
                          reset=True) -> 'XPathConstructor':
        """
        Realiza a navegação e o clique em uma ação específica de menu no
        SIScan, simulando a interação de usuário com menus suspensos
        (dropdown).

        O método localiza o menu principal pelo texto exibido, faz o hover para
        exibir o submenu e, em seguida, busca e clica no item do submenu
        correspondente ao texto da ação desejada. É utilizada tolerância para
        delays de interface, e exceções são disparadas caso o menu principal
        ou a ação não sejam encontrados.

        Parâmetros
        ----------
        menu_name : str
            Texto do menu principal (label) a ser localizado e acionado.
        menu_action_text : str
            Texto do item de submenu (ação) a ser localizado e clicado.
        timeout : int, opcional (default=5)
            Tempo máximo, em segundos, para aguardar a visibilidade do submenu
            antes de falhar.
        reset : bool, opcional (default=True)
            Se True, reseta o estado interno do XPathConstructor após a
            operação.

        Retorno
        -------
        self : XPathConstructor
            Permite encadeamento de métodos.

        Exceções
        --------
        SiscanMenuNotFoundError
            Disparada caso o menu principal ou a ação de menu não sejam
            localizados na página.

        Exemplos
        --------
        ```python
        xpath = XPathConstructor(page)
        xpath.click_menu_action("Paciente", "Pesquisar Paciente")
        ```

        Notas
        -----
        O método depende de seletores de classe CSS específicos
        (exemplo: `.rich-ddmenu-label`, `.rich-menu-item-label`), típicos da
        interface SIScan baseada em RichFaces.
        Em cenários com múltiplos menus ou menus dinâmicos, recomenda-se
        garantir a unicidade dos textos informados.

        """
        page = self.page

        logger.debug(f"Verfica menu: '{menu_name}' existe.")
        # Localiza o menu principal pelo texto
        menu_label = page.locator(
            '.rich-ddmenu-label .rich-label-text-decor',
            has_text=menu_name)
        if menu_label.count() == 0:
            raise SiscanMenuNotFoundError(self.context, menu_name=menu_name)

        logger.debug(f"Verifica se submenu: '{menu_action_text}' existe")
        submenu = page.locator('.rich-menu-item-label',
                               has_text=menu_action_text)
        if submenu.count() == 0:
            raise SiscanMenuNotFoundError(self.context,
                                          menu_name=menu_name,
                                          action=menu_action_text)

        logger.debug(f"Clinca no menu {menu_name} e verifica se o "
                     f"submenu {menu_action_text} está visível")

        interval = self.ELAPSED_INTERVAL
        elapsed = 0
        while elapsed < timeout:
            menu_label.first.hover()
            if submenu.is_visible():
                break
            time.sleep(interval)
            elapsed += interval

        # Delay para submenu aparecer em 500 milissegundo
        # page.wait_for_timeout(timeout*100)

        # Localiza o item do submenu pelo texto e clica

        # submenu.first.wait_for(state="visible",
        #                        timeout=timeout*self.TIMEOUT_MS_FACTOR)
        submenu.first.click(timeout=timeout*self.TIMEOUT_MS_FACTOR)
        logger.debug(f"Menu '{menu_name}' > '{menu_action_text}' acionado.")
        if reset:
            self.reset()
        return self

    def on_blur(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Dispara o evento 'blur' no elemento identificado pelo XPath atual.

        Este método pode ser utilizado para simular a perda de foco em campos
        de formulário, acionando validações client-side ou eventos JavaScript.

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo de espera, em segundos, até o elemento estar visível.
            O padrão é 10 segundos.

        Retorno
        -------
        self : XPathConstructor
            Permite encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath.on_blur()
        ```
        """
        locator = self.wait_and_get(timeout)
        logger.debug(f"Disparando evento 'blur' no elemento localizado por "
                     f"XPath: {self._xpath}")
        locator.dispatch_event('blur')
        return self  # Permite encadeamento, se necessário

    def fill_form_fields(
        self,
        data: dict,
        campos_map: dict[str, tuple[str, str, str]]
    ):
        """
        Preenche automaticamente os campos de um formulário de acordo com
        o mapeamento informado, suportando diferentes tipos de input.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário,
            onde as chaves são os nomes dos campos e os valores são os dados.

        campos_map : dict[str, tuple[str, str, str]]
            Dicionário de mapeamento dos campos permitidos para preenchimento.
            As chaves correspondem aos nomes dos campos e os valores devem ser
            tuplas contendo (label:str, type_input:str, requirement_level:str),
             em que:
              - label: texto do label associado ao campo no formulário.
              - type_input: tipo do campo (ex: InputType.TEXT,
                InputType.SELECT, InputType.CHECKBOX).
              - requirement_level: se "required" ou "optional"

        Exceções
        --------
        TypeError
            É lançada se algum valor do `campos_map` não for uma tupla de três
            strings, indicando erro na configuração do mapeamento.

        Exemplo
        -------
        ```python
        campos_map = {
        ...     "nome": ("Nome:", InputType.TEXT, "required"),
        ...     "sexo": ("Sexo:", InputType.CHECKBOX, "required"),
        ...     "escolaridade": ("Nacionalidade:", InputType.SELECT,
        "optional")
        ... }
        data = {
        ...     "nome": "Maria",
        ...     "sexo": "F",
        ...     "escolaridade": "01"
        ... }
        xpath.fill_form_fields(data, campos_map)
        ```
        """
        for nome_campo, valor in data.items():
            if nome_campo not in campos_map:
                logger.warning(f"Campo '{nome_campo}' não está mapeado "
                               f"ou não é editável. Ignorado.")
                continue

            # Verificação do tipo esperado
            campo_info = campos_map[nome_campo]
            if not (isinstance(campo_info, tuple) and len(campo_info) == 3
                    and all(isinstance(x, str) for x in campo_info)):
                raise TypeError(
                    f"O valor de campos_map['{nome_campo}'] deve ser uma "
                    f"tupla (label:str, type_input:str, requirement_level:str)"
                    f", mas foi recebido: {campo_info!r}"
                )

            label, type_input, _ = campo_info
            self.find_form_input(label, type_input).fill(
                str(valor), type_input)

    def get_select_options(
            self, min_options: int = 2,
            timeout: float = DEFAULT_TIMEOUT,
            interval: float = None) -> dict[str, str]:
        """
        Retorna um dicionário com todas as opções de um campo <select>.

        Este método localiza o elemento <select> associado ao XPath corrente
        e extrai todas as opções disponíveis, retornando um dicionário onde
        cada chave é o atributo 'value' do <option> e o valor é o texto
        apresentado ao usuário.

        Aguarda até que o <select> possua pelo menos 'min_options' opções
        visíveis, tolerando carregamento dinâmico (AJAX).

        Parâmetros
        ----------
        timeout : int, opcional
            Tempo máximo para aguardar o <select> estar visível e carregado,
            em segundos. Padrão: 10 segundos.
        min_options : int, opcional
            Número mínimo de opções para considerar o select carregado.
            Padrão: 2.

        Retorno
        -------
        dict[str, str]
            Dicionário {value: texto_opcao} para todas as opções do campo.

        Exemplo
        -------
        ```
        xpath.find_form_input("Unidade de Saúde", InputType.SELECT)
        options = xpath.get_select_options()
        print(options["4"])
        # '0015466 - CENTRO DE ESPECIALIDADES MEDICAS ENCANTAR'
        ```

        Exceções
        --------
        TimeoutError
            Se o select não carregar o número mínimo de opções no tempo limite.
        """
        locator = self.wait_and_get(timeout)
        interval = interval or self.ELAPSED_INTERVAL
        elapsed = 0
        # Aguarda o select carregar as opções mínimas
        while elapsed < timeout:
            option_count = locator.locator("option").count()
            if option_count >= min_options:
                break
            time.sleep(interval)
            elapsed += interval
        else:
            raise TimeoutError(
                f"Select não carregou pelo menos {min_options} opções após "
                f"{timeout * self.TIMEOUT_MS_FACTOR} milessegundos."
            )

        options_dict = {}
        options = locator.locator("option")
        count = options.count()
        for i in range(count):
            option = options.nth(i)
            value = option.get_attribute("value")
            label = option.inner_text().strip()
            options_dict[value] = label
        return options_dict

    def wait_for_label_visible(self, label_text: str,
                               timeout: float = DEFAULT_TIMEOUT,
                               interval: float = None) -> bool:
        """
        Aguarda até que o label de um campo dependente esteja visível na página.
        Pode ser implementado como método da própria classe.

        Parâmetros
        ----------
        label_text : str
            Texto exato do label esperado.
        timeout : float
            Tempo máximo para aguardar o label (segundos).
        interval : float
            Intervalo entre tentativas (segundos).

        Retorno
        -------
        bool
            True se o label for localizado dentro do timeout, False caso contrário.
        """
        elapsed = 0
        interval = interval or self.ELAPSED_INTERVAL
        selector = f"//label[normalize-space(text())='{label_text}']"
        while elapsed < timeout:
            if self.page.locator(selector).count() > 0:
                return True
            time.sleep(interval)
            elapsed += interval
        self.reset()
        return False


def log(xpath_constructor: XPathConstructor):
    logger.debug('\n' + xpath_constructor.xpath)

