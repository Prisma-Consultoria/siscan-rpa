from utils import messages as msg


class SiscanException(Exception):
    """
    Exceção base para falhas no SIScan.
    Permite extrair mensagens de erro da página Playwright.
    """
    def __init__(self, ctx, m=None):
        self.ctx = ctx
        self.msg = m or ""
        if ctx is not None:
            self.msg = f"{self.msg}. {self.get_error_messages(ctx)}"

        super().__init__(self.msg)

    @classmethod
    def get_error_messages(cls, ctx):
        """
        Busca mensagens de erro padrão na página atual do contexto Playwright.

        Retorna
        -------
        str ou None
            Mensagem de erro concatenada, se encontrada.
        """
        # Seletores tradicionais e de tabela de mensagens de erro
        seletores = [
            '.mensagem-erro',
            '.alert-danger',
            '.mensagem',
            'tr.errorMessage > td'
        ]
        mensagens = []
        for seletor in seletores:
            elementos = ctx.page.query_selector_all(seletor)
            for el in elementos:
                texto = el.inner_text().strip()
                if texto:
                    mensagens.append(texto)
        if mensagens:
            return f"Form Errors: {' | '.join(mensagens)}"
        return ""


class SiscanLoginError(SiscanException):
    """
    Exceção disparada em caso de falha de login no SIScan.
    """
    def __init__(self, ctx, m=None):
        super().__init__(ctx, m or msg.LOGIN_FAIL)


class SiscanMenuNotFoundError(SiscanException):
    """
    Exceção disparada quando um menu ou ação de menu não é encontrado no SIScan.
    """
    def __init__(self, ctx, menu_name: str = None, action: str = None, m: str = None):
        if m is not None:
            mensagem = m
        elif menu_name and action:
            mensagem = msg.MENU_ACTION_NOT_FOUND(menu_name, action)
        elif menu_name:
            mensagem = msg.MENU_NOT_FOUND(menu_name)
        else:
            mensagem = msg.MENU_OR_ACTION_NOT_FOUND
        super().__init__(ctx, mensagem)


class CartaoSusNotFoundError(SiscanException):
    """
    Exceção disparada quando o Cartão SUS informado não é localizado no SIScan.
    """
    def __init__(self, ctx, cartao_sus: str = None, m: str = None):
        if m is not None:
            mensagem = msg
        elif cartao_sus:
            mensagem = msg.CARTAO_SUS_NOT_FOUND_VAL(cartao_sus)
        else:
            mensagem = msg.CARTAO_SUS_NOT_FOUND
        super().__init__(ctx, mensagem)


class PacienteDuplicadoException(SiscanException):
    """
    Exceção disparada quando mais de um paciente é encontrado na busca do SIScan,
    impossibilitando a seleção automática e exigindo intervenção manual.
    """
    def __init__(self, ctx, m: str = None):
        if m is not None:
            mensagem = m
        else:
            mensagem = msg.MULTIPLE_PATIENTS
        super().__init__(ctx, mensagem)


class XpathNotFoundError(SiscanException):
    """
    Exceção disparada quando um elemento (Locator) não é encontrado ou
    não pode ser resolvido na página do SIScan.
    """
    def __init__(self, ctx, xpath: str = None, m: str = None):
        if m is not None:
            mensagem = m
        elif xpath:
            mensagem = msg.XPATH_NOT_FOUND_VAL(xpath)
        else:
            mensagem = msg.XPATH_NOT_FOUND
        super().__init__(ctx, mensagem)


class FieldValueNotFoundError(SiscanException):
    """
    Exceção lançada quando o valor preenchido/selecionado em um campo de
    formulário não corresponde a nenhuma opção válida definida no mapeamento
    FIELDS_MAP. Isto é, o valor fornecido para um select, radio ou checkbox
    não consta entre as opções disponíveis.
    """
    def __init__(self, context, field_name: str, value, m: str | None = None):
        mensagem = m or msg.FIELD_VALUE_NOT_FOUND(field_name, value)
        super().__init__(context, msg=mensagem)
        self.field_name = field_name
        self.value = value


class SiscanInvalidFieldValueError(SiscanException):
    """
    Exceção lançada para indicar que o valor fornecido a um campo do
    formulário SIScan é inválido, inconsistente com as opções permitidas
    ou não está em conformidade com as regras do fluxo de preenchimento.

    Situações em que esta exceção é lançada:
    ----------------------------------------

    1. Quando o valor informado em `data` para um campo não consta na lista
       de opções válidas definidas em `FIELDS_MAP` (exemplo: campo select,
       radio ou checkbox recebeu valor inexistente nas opções do campo).
       - Exemplo: Selecionar uma unidade requisitante cujo código não
            exista no select.
       - Exemplo: Informar um valor de "escolaridade" não cadastrado nas
            opções.

    2. Quando o valor selecionado para um campo do tipo select ou radio
       corresponde ao valor padrão "0" (indicando nenhuma seleção válida).
       - Exemplo: Selecionar um prestador/unidade requisitante e o valor
            retornado for "0".

    3. Quando um campo obrigatório não for informado ou estiver vazio.
       - Exemplo: Campo "cartao_sus" não preenchido.
       - Exemplo: Qualquer campo obrigatório que não foi incluído no
            dicionário de dados.

    4. Quando há tentativa de preenchimento inconsistente entre campos
       relacionados.
       - Exemplo: Campo "Ano que fez a última mamografia" foi preenchido
            mesmo com resposta "Não" para "Fez mamografia alguma vez?".
       - Exemplo: No campo "tem_nodulo_ou_caroco_na_mama", se marcada a
            opção "Não" ("04"), não pode haver outras opções marcadas.

    5. Quando um campo do tipo lista (checkboxes múltiplos) é informado,
       mas nenhum dos valores está entre as opções válidas.

    6. Quando qualquer campo, obrigatório ou não, recebe um valor vazio ou
       None, contrariando as regras de negócio.

    Parâmetros
    ----------
    context : SiscanBrowserContext
        Contexto de execução atual (pode ser None em casos de validação
        isolada).
    field_name : str, opcional
        Nome lógico do campo onde ocorreu o erro.
    data : dict, opcional
        Dicionário de dados submetidos, utilizado para identificar o valor
        problemático.
    options_values : list, opcional
        Lista de valores válidos para o campo, utilizada para construção
        da mensagem de erro.
    message : str, opcional
        Mensagem customizada de erro. Se fornecida, sobrescreve as
        mensagens padrão.

    """

    def __init__(self, context,
                 field_name: str | None = None,
                 data: dict | None = None,
                 options_values: list | None = None,
                 message: str | None = None
                 ):
        if data and field_name and options_values:
            m = msg.INVALID_FIELD_VALUE_OPTIONS(
                field_name,
                data.get(field_name),
                options_values,
            )
        elif field_name:
            m = msg.FIELD_REQUIRED(field_name)
        if message:
            m = message

        super().__init__(context, m)
        self.field_name = field_name
