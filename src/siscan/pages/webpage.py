from abc import abstractmethod, ABC

import logging
import time
from typing import Optional, Callable, Any

from playwright.sync_api import Browser, Page, TimeoutError

from src.siscan.pages.context import SiscanBrowserContext
from src.siscan.pages.utils.xpath_constructor import XPathConstructor
from src.siscan.pages.exception import SiscanLoginError, \
    SiscanMenuNotFoundError, PacienteDuplicadoException, SiscanException, \
    CartaoSusNotFoundError

logger = logging.getLogger(__name__)


class SiscanWebPage (ABC):
    MAP_DATA_FIND_CARTAO_SUS = {
        "cartao_sus": ("Cartão SUS", "text"),
        "cpf": ("CPF", "text"),
        "nome": ("Nome", "text"),
        "nome_da_mae": ("Nome da Mãe", "text"),
        "data_de_nascimento": ("Data de Nascimento", "date"),
        "nacionalidade": ("Nacionalidade", "select"),
        "sexo": ("Sexo", "checkbox"),
    }
    MAP_DATA_CARTAO_SUS = {
        "raca_cor": ("Raça/Cor", "text"),
        "uf": ("UF", "text"),
        "municipio": ("Município", "text"),
        "tipo_logradouro": ("Tipo Logradouro", "text"),
        "nome_logradouro": ("Nome Logradouro", "text"),
        "numero": ("Numero", "text"),
        "bairro": ("Bairro", "text"),
        "cep": ("Cep", "text"),
    }
    MAP_DATA_CARTAO_SUS.update(MAP_DATA_FIND_CARTAO_SUS)
    # Remover CPF pois não é necessário no formulário
    MAP_DATA_CARTAO_SUS.pop("cpf", None)

    # Mapeamento de campos para valores específicos
    FIELDS_MAP = {
        "sexo": {
            "Masculino": "M",
            "Feminino": "F",
        },
        "escolaridade": {
            "Selecione...": "0",
            "Analfabeto(a)": "1",
            "Ensino Fundamental Incompleto": "2",
            "Ensino Fundamental Completo": "3",
            "Ensino Médio Completo": "4",
            "Ensino Superior Completo": "5",
        },
        "tipo_exame_colo": {
            "Cito de Colo...": "02",
            "Histo de Colo": "04",
        },
        "tipo_exame_mama": {
            "Mamografia": "01",
            "Cito de Mama": "03",
            "Histo de Mama": "05",
        }
    }

    def __init__(self, url_base: str):
        self._url_base = url_base
        self._context: Optional[SiscanBrowserContext] = None

    @property
    def context(self) -> SiscanBrowserContext:
        """
        Retorna o contexto Playwright associado a esta instância.
        """
        if self._context is None:
            self._initialize_context()
        return self._context

    def _initialize_context(self):
        self._context = SiscanBrowserContext(
            url_base=self._url_base,
            headless=False,  # Para depuração, use False
            timeout=15000
        )

    @abstractmethod
    def get_map_label(self) -> dict[str, tuple[str, str]]:
        """
        Método abstrato que deve ser implementado por subclasses para retornar
        o mapeamento de labels.
        Deve retornar um dicionário onde as chaves são os nomes dos campos e
        os valores são tuplas contendo o label e o tipo do campo.
        """
        raise NotImplementedError("Subclasses devem implementar este método.")

    def _get_label(
            self, campo: str,
            map_label: Optional[dict[str, tuple[str, str]]] = None) -> str:

        if map_label is None:
            value = self.get_map_label().get(campo)
        else:
            value = map_label.get(campo)

        if value is None:
            raise ValueError(f"Campo '{campo}' não está mapeado.")
        return value[0]

    def _get_label_type(
            self, campo: str,
            map_label: Optional[dict[str, tuple[str, str]]] = None) -> str:
        if map_label is None:
            value = self.get_map_label().get(campo)
        else:
            value = map_label.get(campo)

        if value is None:
            raise ValueError(f"Campo '{campo}' não está mapeado.")
        return value[1]

    def _get_value(self, campo: str, data: dict) -> Optional[str]:
        """
        Obtém o valor de um campo específico do dicionário de dados.

        Parâmetros
        ----------
        campo : str
            Nome do campo a ser buscado.
        data : dict
            Dicionário contendo os dados.

        Retorna
        -------
        Optional[str]
            O valor do campo se existir, caso contrário None.
        """
        value = data.get(campo, None)

        if campo in self.FIELDS_MAP.keys() and value is not None:
            # Mapeia o valor do campo para o valor específico definido no
            # mapeamento
            value = self.FIELDS_MAP[campo].get(value, None)
        return value

    def update_field_map_from_select(
            self,
            field_name: str,
            xpath: XPathConstructor,
            label_as_key: bool = True,
            timeout: int = 10
    ) -> None:
        """
        Atualiza o dicionário FIELDS_MAP[field_name] com opções do select da página.

        Este método utiliza um XPathConstructor já posicionado no campo <select>,
        recupera todas as opções (value, texto) e as insere em FIELDS_MAP para
        permitir mapeamento automático no preenchimento do formulário.

        Parâmetros
        ----------
        field_name : str
            Nome do campo no dicionário FIELDS_MAP a ser atualizado.
        xpath : XPathConstructor
            Instância já posicionada no <select> desejado.
        label_as_key : bool, opcional
            Se True (padrão), usa o texto do option como chave do dicionário
            e o value como valor. Se False, inverte (útil para selects onde
            o backend exige a chave como value).
        timeout : int, opcional
            Tempo máximo para aguardar o <select> na página.

        Retorno
        -------
        None

        Exemplo
        -------
        ```python
        xpath.find_form_input("Unidade de Saúde", "select")
        self.update_field_map_from_select("unidade_saude", xpath)
        print(self.FIELDS_MAP["unidade_saude"])
        {'0015466 - CENTRO DE ...': '4', ...}
        ```
        """
        options = xpath.get_select_options(timeout=timeout)
        if label_as_key:
            mapping = {label: value for value, label in options.items()}
        else:
            mapping = {value: label for value, label in options.items()}
        self.FIELDS_MAP[field_name] = mapping
        xpath.reset()

    def authenticate(self, email: str, senha: str):
        """
        Realiza login no SIScan utilizando um contexto.

        Parâmetros
        ----------
        email : str
            E-mail do usuário SIScan.
        senha : str
            Senha do usuário SIScan.
        ctx : SiscanBrowserContext
            Contexto de execução Playwright.

        Exceções
        --------
        Exception se autenticação falhar.
        """
        self.context.goto('/login.jsf', wait_until='load')

        # Aguarda possível popup abrir e fecha se necessário
        self.context.collect_information_popup()

        xpath = XPathConstructor(self.context)
        xpath.find_form_input('E-mail:').fill(email)
        xpath.find_form_input('Senha:').fill(senha)
        xpath.find_form_button("Acessar").click()

        # Aguarda confirmação de login bem-sucedido
        try:
            self.context.page.wait_for_selector(
                'h1:text("SEJA BEM VINDO AO SISCAN")', timeout=10_000)
        except Exception:
            raise SiscanLoginError(self.context)

    def access_menu(self, menu_name: str, menu_action_text: str,
                    timeout: int = 10, interval: float = None):
        """
        Acessa um menu específico no SIScan, com tentativas automáticas até
        sucesso ou atingir o tempo limite.

        Parâmetros
        ----------
        menu_name : str
            Nome do menu a ser acessado.
        menu_action_text : str
            Texto da ação do menu a ser executada.
        timeout : int, opcional (default=XPathConstructor.RETRY_INTERVAL)
            Tempo máximo, em segundos, para tentar acessar o menu.
        interval : float, opcional (default=)
            Intervalo (em segundos) entre tentativas.

        Exceções
        --------
        SiscanMenuNotFoundError
            Se o menu ou ação não for encontrado após todas as tentativas.
        """
        interval = interval if interval is not None \
            else XPathConstructor.RETRY_INTERVAL

        elapsed = 0
        last_exception = None
        while elapsed < timeout:
            try:
                xpath = XPathConstructor(self.context)
                xpath.click_menu_action(menu_name, menu_action_text)
                logger.info(
                    f"Acesso ao menu '{menu_name} > {menu_action_text}' "
                    "realizado com sucesso."
                )
                return  # Sucesso
            except SiscanMenuNotFoundError as e:
                last_exception = e
                logger.warning(
                    f"Tentativa de acesso ao menu '{menu_name} > "
                    f"{menu_action_text}' falhou ({elapsed:.1f}s). Retentando..."
                )
                time.sleep(interval)
                elapsed += interval
            except Exception as e:
                logger.error(
                    f"Erro inesperado ao acessar menu '{menu_name} > "
                    f"{menu_action_text}': {e}"
                )
                raise SiscanMenuNotFoundError(
                    self.context,
                    menu_name=menu_name,
                    action=menu_action_text,
                    msg=str(e)
                ) from e

        # Todas as tentativas falharam
        logger.error(
            f"Falha definitiva ao acessar menu '{menu_name} > "
            f"{menu_action_text}' após {timeout} segundos."
        )
        raise last_exception if last_exception else SiscanMenuNotFoundError(
            self.context,
            menu_name=menu_name,
            action=menu_action_text,
            msg="Menu não localizado após múltiplas tentativas."
        )

    def mount_fields_map_and_data(
            self, data: dict,
            map_label: dict[str, tuple[str, str]],
            suffix: Optional[str] = ":"
    ) -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
        """
        Gera o dicionário campos_map e o dicionário data_final para uso em
        preenchimento genérico de formulários.

        Parâmetros
        ----------
        data : dict
            Dicionário de dados originais (nomes de campos como chave).
        map_label : dict[str, tuple[str, str]]
            Dicionário com nomes de campos como chave e tuplas contendo
            (label, tipo de campo) como valor.
        suffix : str, opcional (default=":")

        Retorna
        -------
        tuple (campos_map, data_final)
            - campos_map: dict[str, tuple[str, str]]
            - data_final: dict[str, str]
        """
        if suffix is None:
            suffix = ""

        fields_map = {}
        data_final = {}
        for nome_campo in data.keys():
            if nome_campo not in map_label.keys():
                logger.warning(f"Campo '{nome_campo}' não está mapeado ou não "
                               f"é editável. Ignorado.")
                continue
            label = f"{self._get_label(nome_campo, map_label)}{suffix}"
            type_input = self._get_label_type(nome_campo, map_label)
            valor = self._get_value(nome_campo, data)
            fields_map[nome_campo] = (label, type_input)
            data_final[nome_campo] = valor
        return fields_map, data_final

    def select_unique_patient(self, timeout=10):
        """
        Verifica se existe apenas um paciente na tabela de resultados e, se sim, clica em 'Selecionar Paciente'.
        Se houver mais de um, lança PacienteDuplicadoException.
        """
        # Espera a tabela de resultados estar visível
        self.context.page.wait_for_selector("table#frm\\:listaPaciente", state="visible", timeout=timeout * 1000)

        # Localiza o corpo da tabela
        rows = self.context.page.locator("table#frm\\:listaPaciente > tbody > tr")
        row_count = rows.count()
        if row_count > 1:
            raise PacienteDuplicadoException(self.context)
        elif row_count == 0:
            raise Exception("Nenhum paciente encontrado na tabela de resultados.")

        # Se chegou aqui, só há um resultado: clicar no botão 'Selecionar Paciente' (última coluna)
        botao_selecionar = rows.nth(0).locator("a[title='Selecionar Paciente']")
        botao_selecionar.click()

    def _find_cartao_sus(self, data: dict, menu_action: Callable[[], Any]):
        """
        Realiza a busca de um paciente pelo Cartão SUS no SIScan.
        Método para buscar um paciente pelo Cartão SUS, preenchendo os campos de busca e selecionando o paciente.
        Parâmetros
        ----------
        :param data: Dicionário com os dados do paciente a serem buscados.
        :param menu_action: Função que retorna o XPathConstructor configurado para a ação de menu de busca.
        :return: None
        """
        xpath = menu_action()
        xpath.find_search_link_after_input(
            self._get_label("cartao_sus")).click()
        xpath.wait_page_ready()

        # Preenche os campos de busca do Cartão SUS
        fields_map, data_final = self.mount_fields_map_and_data(
            data, self.MAP_DATA_FIND_CARTAO_SUS)
        xpath.fill_form_fields(data_final, fields_map)

        # Clica no botão de buscar
        xpath.find_form_button("Pesquisar").click(
            wait_for_selector="table#frm\\:listaPaciente")

        self.select_unique_patient()

    def fill_cartao_sus(
            self,
            numero: str,
            timeout: int = 10,
            interval: float =None
    ):
        """
        Preenche o campo Cartão SUS no formulário e trata possíveis erros.
        Repete as tentativas de preenchimento e validação até sucesso ou
        até atingir o tempo limite. Se ocorrer erro (mensagem exibida na
        tela) ou o campo 'Nome' for preenchido, interrompe o loop.

        Parâmetros
        ----------
        numero : str
            Número do Cartão SUS a ser preenchido.
        timeout : int, opcional (default=XPathConstructor.RETRY_INTERVAL)
            Tempo máximo, em segundos, para tentar a validação.
        interval : float, opcional (default=0.2)
            Intervalo, em segundos, entre tentativas.

        Exceções
        --------
        CartaoSusNotFoundError
            Disparada se for exibida mensagem de erro na página.
        TimeoutError
            Disparada se não for possível validar/preencher o Cartão SUS
            no tempo limite.
        """
        xpath = XPathConstructor(self.context)
        xpath.wait_page_ready()
        elapsed = 0

        interval = interval if interval is not None \
            else XPathConstructor.RETRY_INTERVAL

        while elapsed < timeout:
            xpath.reset()
            cartao_sus_ele = xpath.find_form_input(
                self._get_label("cartao_sus")).wait_until_enabled()
            cartao_sus_ele.fill(numero, reset=False)
            cartao_sus_ele.on_blur()
            cartao_sus_ele.reset()
            xpath.wait_page_ready()

            # 1. Verifica se há mensagem de erro na página
            message_erros = SiscanException.get_error_messages(self.context)
            if message_erros:
                raise CartaoSusNotFoundError(self.context, cartao_sus=numero)

            # 2. Verifica se o campo "Nome" foi preenchido
            try:
                xpath.reset()
                nome_ele = xpath.find_form_input('Nome')
                nome_ele.wait_until_filled(
                    timeout=interval * xpath.WAIT_FILLED_MULTIPLIER)
                nome = nome_ele.get_value()
                if nome:
                    return  # Sucesso!
            except Exception as err:
                try:
                    current_value = cartao_sus_ele.get().input_value()
                    if current_value:
                        break
                except Exception:
                    logger.warning(f"Erro ao obter valor do campo "
                                   f"Cartão SUS: {numero}. Error: {err}. " 
                                   f"Tentando novamente...")

            # 3. Aguarda o intervalo antes da próxima tentativa
            time.sleep(interval)
            elapsed += interval

