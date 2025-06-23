# Validation messages
def E_REQUIRED(f):
    return f"Campo '{f}' obrigatório"

def E_PATTERN(f, v, p):
    return f"Campo '{f}' com valor '{v}' não corresponde ao padrão '{p}'"

def E_ENUM(f, v, opts):
    return f"Campo '{f}' com valor '{v}' não está entre os valores permitidos: {opts}"

def E_CONDITIONAL(fr, ft, tv):
    return (
        f"O campo '{fr}' tornou-se obrigatório porque o campo '{ft}' foi informado com o valor '{tv}'."
    )

def E_MAX_ITEMS(f, v, inst):
    return (
        f"Quando o valor do campo '{f}' for '{v}', apenas ele deve constar na lista. Foir informado '{inst}'."
    )

M_001 = "Operação concluída"
W_001 = "Aviso"

# API messages
USER_CREATED = "user created"
ERR_USERNAME_PASSWORD_REQUIRED = "username and password required"
ERR_USERNAME_EXISTS = "username already exists"

# Exception messages
LOGIN_FAIL = "Falha na autenticação do SIScan."

def MENU_ACTION_NOT_FOUND(menu, action):
    return f"Menu '{menu}' com ação '{action}' não encontrado no SIScan."

def MENU_NOT_FOUND(menu):
    return f"Menu '{menu}' não encontrado no SIScan."

MENU_OR_ACTION_NOT_FOUND = "Menu ou ação de menu não encontrado no SIScan."

def CARTAO_SUS_NOT_FOUND_VAL(cs):
    return f"Não existe paciente com o Cartão SUS informado: {cs}."

CARTAO_SUS_NOT_FOUND = "Não existe paciente com o Cartão SUS informado."
MULTIPLE_PATIENTS = (
    "Foram encontrados múltiplos pacientes na busca. A seleção não pode ser realizada automaticamente."
)

def XPATH_NOT_FOUND_VAL(xp):
    return f"Elemento com XPath '{xp}' não encontrado ou não resolvível na página do SIScan."

XPATH_NOT_FOUND = "Elemento não encontrado ou não resolvível na página do SIScan."

def FIELD_VALUE_NOT_FOUND(field, value):
    return (
        f"Valor '{value}' não encontrado na lista de opções válidas para o campo '{field}'."
    )

def INVALID_FIELD_VALUE_OPTIONS(field, value, opts):
    return (
        f"O valor '{value}' fornecido para o campo '{field}' não consta na lista de opções válidas. Opções válidas: {', '.join(opts)}."
    )

def FIELD_REQUIRED(field):
    return f"O campo '{field}' deve ser informado."

# Other domain messages
MENU_ACCESS_TIMEOUT = "Menu não localizado após múltiplas tentativas."
ANO_MAMOGRAFIA_REQUIRED = (
    "Campos 'Ano' de 'QUANDO FEZ A ÚLTIMA MAMOGRAFIA?' do card 'FEZ MAMOGRAFIA ALGUMA VEZ?' é obrigatório."
)
ANO_RADIOTERAPIA_REQUIRED = "Campos de ano da radioterapia obrigatórios conforme a localização."
CARTAO_SUS_NAO_INFORMADO = "Cartão SUS não informado."
CONTEXT_NOT_INITIALIZED = "Contexto não inicializado."

__all__ = [name for name in globals() if name.isupper()]
