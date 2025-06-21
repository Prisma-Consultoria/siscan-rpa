class SiscanException(Exception):
    """
    Exceção base para falhas no SIScan.
    Permite extrair mensagens de erro da página Playwright.
    """
    def __init__(self, ctx, msg=None):
        self.ctx = ctx
        self.msg = msg or ""
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
    def __init__(self, ctx, msg=None):
        super().__init__(ctx, msg or "Falha na autenticação do SIScan.")


class SiscanMenuNotFoundError(SiscanException):
    """
    Exceção disparada quando um menu ou ação de menu não é encontrado no SIScan.
    """
    def __init__(self, ctx, menu_name: str = None, action: str = None, msg: str = None):
        if msg is not None:
            mensagem = msg
        elif menu_name and action:
            mensagem = f"Menu '{menu_name}' com ação '{action}' não encontrado no SIScan."
        elif menu_name:
            mensagem = f"Menu '{menu_name}' não encontrado no SIScan."
        else:
            mensagem = "Menu ou ação de menu não encontrado no SIScan."
        super().__init__(ctx, mensagem)


class CartaoSusNotFoundError(SiscanException):
    """
    Exceção disparada quando o Cartão SUS informado não é localizado no SIScan.
    """
    def __init__(self, ctx, cartao_sus: str = None, msg: str = None):
        if msg is not None:
            mensagem = msg
        elif cartao_sus:
            mensagem = f"Não existe paciente com o Cartão SUS informado: {cartao_sus}."
        else:
            mensagem = "Não existe paciente com o Cartão SUS informado."
        super().__init__(ctx, mensagem)


class PacienteDuplicadoException(SiscanException):
    """
    Exceção disparada quando mais de um paciente é encontrado na busca do SIScan,
    impossibilitando a seleção automática e exigindo intervenção manual.
    """
    def __init__(self, ctx, msg: str = None):
        if msg is not None:
            mensagem = msg
        else:
            mensagem = "Foram encontrados múltiplos pacientes na busca. A seleção não pode ser realizada automaticamente."
        super().__init__(ctx, mensagem)


class XpathNotFoundError(SiscanException):
    """
    Exceção disparada quando um elemento (Locator) não é encontrado ou
    não pode ser resolvido na página do SIScan.
    """
    def __init__(self, ctx, xpath: str = None, msg: str = None):
        if msg is not None:
            mensagem = msg
        elif xpath:
            mensagem = (f"Elemento com XPath '{xpath}' não encontrado "
                        f"ou não resolvível na página do SIScan.")
        else:
            mensagem = ("Elemento não encontrado "
                        "ou não resolvível na página do SIScan.")
        super().__init__(ctx, mensagem)


class FieldValueNotFoundError(SiscanException):
    """
    Exceção lançada quando o valor preenchido/selecionado em um campo de
    formulário não corresponde a nenhuma opção válida definida no mapeamento
    FIELDS_MAP. Isto é, o valor fornecido para um select, radio ou checkbox
    não consta entre as opções disponíveis.
    """
    def __init__(self, context, field_name: str, value, msg: str = None):
        mensagem = (msg or
            f"Valor '{value}' não encontrado na lista de opções válidas para "
            f"o campo '{field_name}'.")
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
                 field_name: str = None,
                 data: dict = None,
                 options_values: list = None,
                 message: str = None
                 ):
        if data and field_name and options_values:
            msg = (
                f"O valor '{data.get(field_name)}' "
                f"fornecido para o campo '{field_name}' não consta na "
                f"lista de opções válidas. "
                f"Opções válidas: {', '.join(options_values)}."
            )
        elif field_name:
            msg = f"O campo '{field_name}' deve ser informado."
        if message:
            msg = message

        super().__init__(context, msg)
        self.field_name = field_name
