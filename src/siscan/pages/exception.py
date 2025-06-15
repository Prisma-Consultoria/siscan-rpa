class SiscanException(Exception):
    """
    Exceção base para falhas no SIScan.
    Permite extrair mensagens de erro da página Playwright.
    """
    def __init__(self, ctx, msg=None):
        self.ctx = ctx
        self.msg = msg or self.get_error_messages(ctx)
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
            return " | ".join(mensagens)
        return None


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