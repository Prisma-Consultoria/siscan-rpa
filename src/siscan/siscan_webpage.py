import re
import time

from jsonschema.exceptions import ValidationError, SchemaError
from pathlib import Path

import logging
from typing import Optional, Callable, Any, Union

from src.siscan.exception import SiscanLoginError, \
    SiscanMenuNotFoundError, PacienteDuplicadoException, SiscanException, \
    CartaoSusNotFoundError, SiscanInvalidFieldValueError
from src.siscan.utils.SchemaMapExtractor import SchemaMapExtractor
from src.siscan.utils.schema_validator import SchemaValidator, \
    SchemaValidationError
from src.siscan.webtools.webpage import WebPage, RequirementLevel
from src.siscan.webtools.xpath_constructor import XPathConstructor, InputType

logger = logging.getLogger(__name__)


class SiscanWebPage(WebPage):
    MAP_DATA_FIND_CARTAO_SUS = [
        "cartao_sus",
        "cpf",
        "nome",
        "nome_da_mae",
        "data_de_nascimento",
        "nacionalidade",
        "sexo"
    ]
    MAP_DATA_CARTAO_SUS = [
        "raca_cor",
        "uf",
        "municipio",
        "tipo_logradouro",
        "nome_logradouro",
        "numero",
        "bairro",
        "cep"
    ]
    MAP_SCHEMA_FIELDS = MAP_DATA_FIND_CARTAO_SUS + MAP_DATA_CARTAO_SUS

    def __init__(self, url_base: str, user: str, password: str,
                 schema_path: Union[str, Path]):
        super().__init__(url_base, user, password, schema_path)
        map_data_label, fields_map = SchemaMapExtractor.schema_to_maps(
            schema_path, fields=SiscanWebPage.MAP_SCHEMA_FIELDS)
        SiscanWebPage.MAP_DATA_LABEL = map_data_label
        self.FIELDS_MAP.update(fields_map)

    def validation(self, data: dict):
        try:
            SchemaValidator.validate_data(data, self.schema_path)
            logger.debug("Dados válidos")
        except SchemaValidationError as ve:
            # Exemplo: acesso aos detalhes
            for campo in ve.required_missing:
                logger.error("Campo obrigatório ausente: %s", campo)
            for err in ve.pattern_errors:
                logger.error("Erro de padrão: %s", err.message)
            for err in ve.enum_errors:
                logger.error("Erro de enum: %s", err.message)
            for field_required, field_trigger, trigger_value in ve.conditional_failure:
                logger.error("Campo condicional: '%s' (devido a '%s' == '%s')",
                             field_required, field_trigger, trigger_value)
            for err in ve.outros_erros:
                logger.error("Outro erro: %s", err.message)

            raise SiscanInvalidFieldValueError(
                context=None,
                data=data,
                message=ve.message
            )

        except ValidationError as ve:
            logger.error(ve)

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
        self.take_screenshot("screenshot_01_autenticar.png")
        xpath.find_form_button("Acessar").click()

        # Aguarda confirmação de login bem-sucedido
        try:
            self.context.page.wait_for_selector(
                'h1:text("SEJA BEM VINDO AO SISCAN")', timeout=10_000)
        except Exception:
            raise SiscanLoginError(self.context)
        self.take_screenshot("screenshot_02_tela_principal.png")

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
            else XPathConstructor.ELAPSED_INTERVAL

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
            timeout: int = XPathConstructor.DEFAULT_TIMEOUT,
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

        interval = interval or (XPathConstructor.ELAPSED_INTERVAL)

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
                nome_ele.wait_until_filled(timeout=timeout)
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
        logger.debug(f"Preenchendo campo '{field_name}' de '{card_name}' "
                     f"com o valor '{value}'")
        # //fieldset[legend[normalize-space(text())='{card_name}']]//input[@type='text']
        # //fieldset[legend[normalize-space(text())='{card_name}']]//label[normalize-space(text())='{field_name}']/@for
        xpath_obj = XPathConstructor(
            self.context,
            xpath=f"//fieldset[legend[normalize-space(text())='{card_name}']]"
                  f"//input[@type='text']"
            # xpath=f"//fieldset[legend[normalize-space(text())='{card_name}']]"
            #       f"//label[normalize-space(text())='{field_name}']"
            #       f"/following-sibling::input[1]"
        )

        xpath_obj.fill(value)

    def preencher_campo_dependente_multiplo(
            self,
            data: dict,
            campo_chave: str,
            condicoes_dependentes: dict,
            label_dependentes: dict = None,
            erro_dependente_msg: str = None
    ):
        logger.debug(f"Selecionar campo {campo_chave}")
        text, value = self.select_value(campo_chave, data)

        dependentes = condicoes_dependentes.get(value, [])
        labels = label_dependentes or {}

        for dep in dependentes:
            valor_dep = data.get(dep)
            if not valor_dep:
                raise SiscanInvalidFieldValueError(
                    context=None,
                    field_name=dep,
                    data=data,
                    message=erro_dependente_msg or
                            f"O campo {dep} é obrigatório para o valor "
                            f"'{text}({value})' do card {campo_chave}."
                )

            # Preencher o campo dependente
            self.fill_field_in_card(
                card_name=self.get_field_label(dep),
                field_name=labels.get(dep),
                value=valor_dep
            )
            data.pop(dep, None)
        data.pop(campo_chave, None)

