import time

import logging
from typing import Optional, Callable, Any

from src.siscan.exception import SiscanLoginError, \
    SiscanMenuNotFoundError, PacienteDuplicadoException, SiscanException, \
    CartaoSusNotFoundError, SiscanInvalidFieldValueError, \
    SiscanRequiredFieldNotProvidedError
from src.siscan.webtools.webpage import WebPage, RequirementLevel
from src.siscan.webtools.xpath_constructor import XPathConstructor, InputType

logger = logging.getLogger(__name__)


class SiscanWebPage(WebPage):
    MAP_DATA_FIND_CARTAO_SUS = {
        "cartao_sus": ("Cartão SUS", InputType.TEXT,
                       RequirementLevel.REQUIRED),
        "cpf": ("CPF", InputType.TEXT, RequirementLevel.OPTIONAL),
        "nome": ("Nome", InputType.TEXT, RequirementLevel.REQUIRED),
        "nome_da_mae": ("Nome da Mãe", InputType.TEXT,
                        RequirementLevel.REQUIRED),
        "data_de_nascimento": ("Data de Nascimento", InputType.DATE,
                               RequirementLevel.REQUIRED),
        "nacionalidade": ("Nacionalidade", InputType.SELECT,
                          RequirementLevel.REQUIRED),
        "sexo": ("Sexo", InputType.CHECKBOX, RequirementLevel.REQUIRED),
    }
    MAP_DATA_CARTAO_SUS = {
        "raca_cor": ("Raça/Cor", InputType.TEXT, RequirementLevel.REQUIRED),
        "uf": ("UF", InputType.TEXT, RequirementLevel.REQUIRED),
        "municipio": ("Município", InputType.TEXT, RequirementLevel.REQUIRED),
        "tipo_logradouro": ("Tipo Logradouro", InputType.TEXT, RequirementLevel.REQUIRED),
        "nome_logradouro": ("Nome Logradouro", InputType.TEXT, RequirementLevel.REQUIRED),
        "numero": ("Numero", InputType.TEXT, RequirementLevel.REQUIRED),
        "bairro": ("Bairro", InputType.TEXT, RequirementLevel.REQUIRED),
        "cep": ("Cep", InputType.TEXT, RequirementLevel.REQUIRED),
    }
    MAP_DATA_CARTAO_SUS.update(MAP_DATA_FIND_CARTAO_SUS)
    # Remover CPF pois não é necessário no formulário
    MAP_DATA_CARTAO_SUS.pop("cpf", None)

    # Mapeamento de campos para valores específicos
    FIELDS_MAP = {
        "sexo": {
            "M": "M",  # Masculino
            "F": "F",  # Feminino
        }
    }

    def validation(self, data: dict):
        for nome_campo in self.FIELDS_MAP.keys():
            _, _, requirement_level = self.get_field_metadata(
                nome_campo
            )
            if nome_campo not in data.keys():
                raise SiscanRequiredFieldNotProvidedError(
                    context=None,
                    field_name=nome_campo
                )
            elif isinstance(data.get(nome_campo), list):
                # Se o campo for uma lista, verifica se algum valor é válido
                if not any(item in self.FIELDS_MAP[nome_campo].keys()
                           for item in data[nome_campo]):
                    raise SiscanInvalidFieldValueError(
                        context=None,
                        field_name=nome_campo,
                        data=data,
                        options_values=self.FIELDS_MAP[nome_campo].keys()
                    )
            elif not data.get(nome_campo) in self.FIELDS_MAP[nome_campo].keys():
                raise SiscanInvalidFieldValueError(
                    context=None,
                    field_name=nome_campo,
                    data=data,
                    options_values=self.FIELDS_MAP[nome_campo].keys()
            )
        for key, value in data.items():
            if not value:
                raise SiscanInvalidFieldValueError(
                    context=None,
                    message="Campo '{key}' não pode estar vazio.")

    def authenticate(self):
        """
        Realiza login no SIScan utilizando um contexto.

        Exceções
        --------
        Exception se autenticação falhar.
        """

        self.context.goto('/login.jsf', wait_until='load')

        # Aguarda possível popup abrir e fecha se necessário
        self.context.collect_information_popup()

        xpath = XPathConstructor(self.context)
        xpath.find_form_input('E-mail:').fill(self._user)
        xpath.find_form_input('Senha:').fill(self._password)
        xpath.find_form_button("Acessar").click()

        # Aguarda confirmação de login bem-sucedido
        try:
            self.context.page.wait_for_selector(
                'h1:text("SEJA BEM VINDO AO SISCAN")', timeout=10_000)
        except Exception:
            raise SiscanLoginError(self.context)

    def acessar_menu(self, menu_name: str, menu_action_text: str,
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
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Tentativa de acesso ao menu '{menu_name} > "
                    f"{menu_action_text}' falhou ({elapsed:.1f}s). "
                    f"Retentando..."
                )
                time.sleep(interval)
                elapsed += interval

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

    def seleciona_um_paciente(self, timeout=10):
        """
        Verifica se existe apenas um paciente na tabela de resultados e, se
        sim, clica em 'Selecionar Paciente'. Se houver mais de um, lança
        PacienteDuplicadoException.
        """
        # Espera a tabela de resultados estar visível
        self.context.page.wait_for_selector("table#frm\\:listaPaciente",
                                            state="visible",
                                            timeout=timeout * 1000)

        # Localiza o corpo da tabela
        rows = self.context.page.locator(
            "table#frm\\:listaPaciente > tbody > tr")
        row_count = rows.count()
        if row_count > 1:
            raise PacienteDuplicadoException(self.context)
        elif row_count == 0:
            raise Exception("Nenhum paciente encontrado na tabela de "
                            "resultados.")

        # Se chegou aqui, só há um resultado: clicar no botão
        # 'Selecionar Paciente' (última coluna)
        botao_selecionar = rows.nth(0).locator(
            "a[title='Selecionar Paciente']")
        botao_selecionar.click()

    def _buscar_cartao_sus(self, data: dict, menu_action: Callable[[], Any]):
        """
        Realiza a busca de um paciente pelo Cartão SUS no SIScan.
        Método para buscar um paciente pelo Cartão SUS, preenchendo os campos
        de busca e selecionando o paciente.
        Parâmetros
        ----------
        :param data: Dicionário com os dados do paciente a serem buscados.
        :param menu_action: Função que retorna o XPathConstructor configurado
               para a ação de menu de busca.
        :return: None
        """
        xpath = menu_action()
        xpath.find_search_link_after_input(
            self.get_field_label("cartao_sus")).click()
        xpath.wait_page_ready()

        # Preenche os campos de busca do Cartão SUS
        fields_map, data_final = self.mount_fields_map_and_data(
            data, self.MAP_DATA_FIND_CARTAO_SUS)
        xpath.fill_form_fields(data_final, fields_map)

        # Clica no botão de buscar
        xpath.find_form_button("Pesquisar").click(
            wait_for_selector="table#frm\\:listaPaciente")

        self.seleciona_um_paciente()

    def preencher_cartao_sus(
            self,
            numero: str,
            timeout: int = 10,
            interval: float = None
    ):
        """
        Preenche o campo Cartão SUS no formulário e trata possíveis erros.
        Repete as tentativas de preenchimento e validação até sucesso ou até
        atingir o tempo limite. Se ocorrer erro (mensagem exibida na tela) ou
        o campo 'Nome' for preenchido, interrompe o loop.

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
                self.get_field_label("cartao_sus")).wait_until_enabled()
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
                    timeout=interval)
                nome, _ = nome_ele.get_value()
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

    def fill_field_in_card(self, card_name: str, field_name: str, value: str):
        xpath_obj = XPathConstructor(
            self.context,
            xpath=f"//fieldset[legend[normalize-space(text())='{card_name}']]"
                  f"//label[normalize-space(text())={field_name}]"
                  f"/following-sibling::input[1]")
        xpath_obj.fill(value)
