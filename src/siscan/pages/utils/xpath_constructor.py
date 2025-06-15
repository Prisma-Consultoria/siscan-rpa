import ast
import time
import logging
from playwright.sync_api import Page, TimeoutError

from src.siscan.pages.context import SiscanBrowserContext
from src.siscan.pages.exception import SiscanMenuNotFoundError, \
    XpathNotFoundError, SiscanException

logger = logging.getLogger(__name__)

INPUT_TYPES = {
    'text': 'input',
    'date': 'input',
    'value': 'input',
    'number': 'input',
    'file': 'input',
    'checkbox': 'input',
    'multiple-checkbox': 'multiplecheckbox',
    'checkbox-popup': 'multiplecheckbox',
    'textarea': 'textarea',
    'list': 'select',
    'select': 'select',
    'tree': 'arvore',
    'radio': 'radio',
    'search': 'busca',
    'autocomplete-list': 'lista autocompletar',
    'multiple-list': 'lista multipla',
    'multiple-autocomplete': 'autocomplete multiplo',
    'filtered-select-multiple': 'filteredselectmultiple',
    'placeholder': 'placeholder',
    'aria-label': 'aria-label'
}


class XPathConstructor:
    # Fator de conversão de segundos para milissegundos
    TIMEOUT_MS_FACTOR = 1000
    # Multiplicador para o tempo de espera
    WAIT_FILLED_MULTIPLIER = 5
    # Intervalo entre tentativas de repetição (em segundos)
    RETRY_INTERVAL = 0.5  # segundos


    """
    Construtor de XPaths reutilizáveis para localizar elementos na página.
    Compatível com Playwright (não usa Selenium).
    """
    def __init__(self, context: SiscanBrowserContext, xpath=''):
        self._page = context.page
        self._browser = context.browser
        self._context = context
        self._xpath = xpath

    def __str__(self):
        return f"XPathConstructor(xpath='{self._xpath}')"
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

    def wait_and_get(self, timeout=10) -> Page.locator:
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
                     f"por {timeout} segundos")
        try:
            # Espera 10 segundos
            locator.wait_for(state="visible",
                             timeout=timeout * self.TIMEOUT_MS_FACTOR)
            return locator
        except TimeoutError:
            # Se o wait_for estourar timeout, o elemento não se tornou visível
            logger.error(f"Timeout: Elemento com XPath '{self._xpath}' "
                         f"não se tornou visível em {timeout} segundos.")
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

    def wait_until_enabled(self, timeout=10):
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
        self.page.wait_for_selector(
            f'xpath={self._xpath}[not(@disabled)]',
            timeout=timeout * self.TIMEOUT_MS_FACTOR)
        return self

    def wait_until_filled(self, timeout=10):
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
                             timeout=timeout*self.TIMEOUT_MS_FACTOR)

            # Em seguida, espera até o atributo 'value' ser diferente de vazio
            logger.debug(
                f"Esperando o campo com XPath '{self._xpath}' "
                f"ter valor preenchido.")
            self.page.wait_for_function(
                """(element) => {
                    return element.value.length > 0;
                }""",
                arg=locator.element_handle(),
                timeout=timeout * self.TIMEOUT_MS_FACTOR * self.WAIT_FILLED_MULTIPLIER
            )
            logger.info(
                f"Campo com XPath '{self._xpath}' foi preenchido com sucesso.")
            return self
        except TimeoutError as e:
            # Captura timeouts do wait_for(state="visible")
            # ou wait_for_function
            logger.error(f"Timeout: O campo '{self._xpath}' não foi "
                         f"preenchido ou não se tornou visível dentro "
                         f"de {timeout} segundos. Erro: {e}")
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

    def wait_page_ready(self, timeout=10) -> 'XPathConstructor':
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
                         f"Timeout: {timeout}s")
            self.page.wait_for_load_state(
                "networkidle", timeout=timeout * self.TIMEOUT_MS_FACTOR)
            logger.debug("Estado 'networkidle' alcançado.")

            # Espera pelo jQuery, caso a aplicação o utilize.
            # Esta verificação é opcional; remova-a se sua aplicação não usa
            # jQuery.
            logger.debug(f"Verificando a disponibilidade do jQuery na página. "
                         f"Timeout: {timeout}s")
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
                         f"carregou dentro de {timeout} segundos. Erro: {e}")
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

    def get_value(self, type_input: str = "texto", timeout=500):
        """
        Obtém o valor do campo localizado pelo XPath corrente, de acordo com o
        tipo do campo informado.

        O método adapta a extração do valor conforme o tipo do campo:
          - Para campos de texto e textarea, retorna o valor digitado.
          - Para campos select, retorna o texto da opção atualmente
            selecionada.
          - Para checkbox e radio, retorna se está marcado (True/False).
          - Para múltiplos checkboxes, retorna uma lista com os valores
            marcados.
          - Para elementos do tipo div ou span, retorna o texto contido no
            elemento.
          - Para outros tipos, utiliza o input_value padrão do Playwright.

        Parâmetros
        ----------
        type_input : str, opcional
            Tipo do campo a ser lido ('texto', 'select', 'checkbox', 'radio',
            'multiple-checkbox', 'div', 'span', etc.). O padrão é 'texto'.
        timeout : int, opcional
            Tempo máximo (em milissegundos) para aguardar o elemento.
            Padrão: 500.

        Retorno
        -------
        valor : str, bool ou list
            O valor extraído do campo, podendo ser string, booleano ou lista de
            strings conforme o tipo do campo.

        Exemplo
        -------
        ```python
        valor = xpath.get_value("select")
        checked = xpath.get_value("checkbox")
        lista = xpath.get_value("multiple-checkbox")
        ```
        """
        locator = self.wait_and_get(timeout)
        input_type = INPUT_TYPES.get(type_input, 'input')

        if input_type in ("text", "textarea"):
            return locator.input_value()
        elif input_type == "select":
            # Retorna o texto visível da opção selecionada
            selected_option = locator.locator('option:checked')
            return selected_option.inner_text().strip()
        elif input_type == "checkbox":
            return locator.is_checked()
        elif input_type == "radio":
            return locator.is_checked()
        elif input_type == "multiple-checkbox":
            # Checkbox múltiplo: retorna lista de valores selecionados
            checkboxes = locator.all()
            return [cb.input_value() for cb in checkboxes if cb.is_checked()]
        elif input_type in ("div", "span"):
            return locator.inner_text().strip()
        else:
            return locator.input_value()  # Padrão

    def find_form_input(self,
                        label_name: str,
                        type_input: str = "text") -> 'XPathConstructor':
        """
        Localiza um campo de formulário (input, textarea, select, data ou
        checkbox) associado a um label específico.

        O método constrói o XPath conforme o tipo de campo:
          - Para campos de data ('date'), procura o input dentro do span
            subsequente.
          - Para campos do tipo checkbox, localiza a tabela após o label
            contendo os inputs do tipo checkbox.
          - Para outros tipos (ex: text, select, textarea), localiza o elemento
            irmão direto do label.

        Parâmetros
        ----------
        label_name : str
            Texto do label do campo a ser localizado.
        type_input : str, opcional
            Tipo do campo a ser localizado (ex: 'text', 'date', 'checkbox',
            'select'). O padrão é 'text'.

        Retorno
        -------
        self : XPathConstructor
            Permite o encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath.find_form_input("CPF:", type_input="text").fill("123...")
        xpath.find_form_input("Sexo:", type_input="checkbox").fill("M")
        ```
        """
        input_type = INPUT_TYPES[type_input]
        label_xpath = f"//label[normalize-space(text())='{label_name}']"

        if type_input == "date":
            # Para campos de data, encontra o span após o label e dentro dele
            # busca o input de texto do calendário
            self._xpath += (
                f"{label_xpath}/following-sibling::span[1]//{input_type}"
                f"[contains(@class, 'date') or contains(@class, 'calendar')]"
            )
        elif type_input == "checkbox":
            # Para checkbox, busca todos os inputs do tipo checkbox após o
            # label, dentro de qualquer estrutura (ex: tabela)
            self._xpath += (
                f"{label_xpath}/following-sibling::table[1]"
            )
        elif type_input == "radio":
            # Para radio: busca no fieldset com legend igual ao label_name
            self._xpath += (
                f"//fieldset[legend[normalize-space(text())='{label_name}']]"
            )
        elif type_input == "select":
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
                f"{label_xpath}/following-sibling::{input_type}[1]"
            )
        logger.debug(f"XPath: {self._xpath}")
        return self

    def _select_option_with_retry(
            self, obj_locator, value: str, timeout=10, interval: float = None):
        """
        Seleciona uma opção de <select> via value, aguardando as opções
        aparecerem se necessário.
        """
        interval = interval if interval is not None else self.RETRY_INTERVAL
        value = ast.literal_eval('None')  # retorna None
        if value is None:
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
        self.find_form_input(label_name, type_input="text")
        # Adiciona o seletor para o <a> logo após o campo
        self._xpath += "/following-sibling::a[1]"
        logger.debug(f"XPath para lupa após input "
                     f"'{label_name}': {self._xpath}")
        return self

    def fill(self, value: str, type_input="texto",
             timeout=10, reset=True) -> 'XPathConstructor':
        """
        Preenche campos de formulário identificados pelo XPath interno.

        Este método preenche automaticamente campos de diferentes tipos,
        selecionando a abordagem correta conforme o tipo informado.

        Parâmetros
        ----------
        valor : str
            Valor a ser preenchido no campo. Para campos checkbox, pode ser
            uma lista de valores a serem marcados/desmarcados.
        type_input : str, opcional
            Tipo do campo: "texto" (padrão), "select", "lista" ou "checkbox".
        timeout : int, opcional
            Tempo máximo, em segundos, para aguardar o campo estar visível.
            Padrão: 10.
        reset : bool, opcional
            Se True, reseta o XPath após preencher o campo. Padrão: True.

        Retorno
        -------
        self : XPathConstructor
            Retorna a própria instância para permitir encadeamento de métodos.

        Exemplo
        -------
        ```python
        xpath.fill("JAILTON PAIVA", type_input="texto")
        xpath.fill("BRASILEIRO", type_input="select")
        xpath.fill(["M", "F"], type_input="checkbox")
        ```

        Observações
        -----------
        - Para campos "select" ou "lista", o valor é selecionado pela opção
          exibida (label).
        - Para "checkbox", marca/desmarca de acordo com os valores informados.
        - Para outros tipos, preenche o campo usando o método fill do
          Playwright.
        """
        locator = self.wait_and_get(timeout)
        logger.debug(
            f"Preenchendo o campo do tipo {type_input} com valor: {value}"
        )
        if type_input in ("select", "lista"):
            if value is None:
                logger.warning(
                    f"Valor vazio para campo do tipo {type_input}. "
                    "Nenhum valor será preenchido.")
                breakpoint()
                return self
            self._select_option_with_retry(locator, value, timeout)
        elif type_input == "checkbox":
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
                    input_el.check(force=True)
                elif input_value not in valores and is_checked:
                    input_el.uncheck(force=True)
        elif type_input == "radio":
            # Para radio: selecionar o radio com value==valor dentro do grupo
            # identificado
            # locator deve ser o grupo (fieldset ou container de radios)
            radios = locator.locator("input[type='radio']")
            count = radios.count()
            achou = False

            for i in range(count):
                radio = radios.nth(i)
                radio_value = radio.get_attribute("value")
                is_checked = radio.is_checked()
                if radio_value == value:
                    logger.debug(
                        f"Marcando radio value={value} (checked={is_checked})")
                    if not is_checked:
                        radio.check(force=True)
                    achou = True
                    break
            if not achou:
                logger.warning(
                    f"Valor '{value}' não encontrado no grupo de radio.")
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
        logger.debug(f"XPath do botão localizado: {self._xpath}")
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

    def click(self, timeout: int = 10, interval: float = None,
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
        interval = interval if interval is not None else self.RETRY_INTERVAL

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
                        timeout=(timeout - elapsed) * self.TIMEOUT_MS_FACTOR
                    )
                if reset:
                    self.reset()
                return self
            except Exception as e:
                time.sleep(interval)
                elapsed += interval
        raise TimeoutError(f'Timeout ao clicar no elemento {self.xpath} após '
                           f'{timeout} segundos.')

    def click_menu_action(self, menu_name: str, menu_action_text: str,
                          timeout: int = 5, reset=True) -> 'XPathConstructor':
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
        logger.debug(f"Buscando menu principal: '{menu_name}'")
        page = self.page

        # Localiza o menu principal pelo texto
        menu_label = page.locator(
            '.rich-ddmenu-label .rich-label-text-decor', has_text=menu_name)
        if menu_label.count() == 0:
            raise SiscanMenuNotFoundError(self.context, menu_name=menu_name)
        menu_label.first.hover()
        page.wait_for_timeout(200)  # Delay para submenu aparecer

        # Localiza o item do submenu pelo texto e clica
        logger.debug(f"Buscando ação do menu: '{menu_action_text}'")
        submenu = page.locator('.rich-menu-item-label',
                               has_text=menu_action_text)
        if submenu.count() == 0:
            raise SiscanMenuNotFoundError(self.context, menu_name=menu_name,
                                          action=menu_action_text)
        submenu.first.wait_for(state="visible",
                               timeout=timeout*self.TIMEOUT_MS_FACTOR)
        submenu.first.click()
        logger.debug(f"Menu '{menu_name}' > '{menu_action_text}' acionado.")
        if reset:
            self.reset()
        return self

    def on_blur(self, timeout=10):
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
        campos_map: dict[str, tuple[str, str]]
    ):
        """
        Preenche automaticamente os campos de um formulário de acordo com
        o mapeamento informado, suportando diferentes tipos de input.

        Parâmetros
        ----------
        data : dict
            Dicionário contendo os dados a serem preenchidos no formulário,
            onde as chaves são os nomes dos campos e os valores são os dados.

        campos_map : dict[str, tuple[str, str]]
            Dicionário de mapeamento dos campos permitidos para preenchimento.
            As chaves correspondem aos nomes dos campos e os valores devem ser
            tuplas contendo (label:str, type_input:str), em que:
              - label: texto do label associado ao campo no formulário.
              - type_input: tipo do campo (ex: "texto", "select", "checkbox").

        Exceções
        --------
        TypeError
            É lançada se algum valor do `campos_map` não for uma tupla de dois
            strings, indicando erro na configuração do mapeamento.

        Exemplo
        -------
        ```python
        campos_map = {
        ...     "nome": ("Nome:", "texto"),
        ...     "sexo": ("Sexo:", "checkbox"),
        ...     "nacionalidade": ("Nacionalidade:", "select")
        ... }
        data = {
        ...     "nome": "Maria",
        ...     "sexo": "F",
        ...     "nacionalidade": "BRASILEIRO"
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
            if not (isinstance(campo_info, tuple) and len(campo_info) == 2
                    and all(isinstance(x, str) for x in campo_info)):
                raise TypeError(
                    f"O valor de campos_map['{nome_campo}'] deve ser uma "
                    f"tupla (label:str, type_input:str), "
                    f"mas foi recebido: {campo_info!r}"
                )

            label, type_input = campo_info
            self.find_form_input(label, type_input).fill(
                str(valor), type_input)

    def get_select_options(
            self, timeout: int = 10, min_options: int = 2) -> dict[str, str]:
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
        >>> xpath.find_form_input("Unidade de Saúde", "select")
        >>> options = xpath.get_select_options()
        >>> print(options["4"])
        '0015466 - CENTRO DE ESPECIALIDADES MEDICAS ENCANTAR'

        Exceções
        --------
        TimeoutError
            Se o select não carregar o número mínimo de opções no tempo limite.
        """
        locator = self.wait_and_get(timeout)
        interval = 0.2
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
                f"{timeout} segundos."
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


def log(xpath_constructor: XPathConstructor):
    logger.debug('\n' + xpath_constructor.xpath)
