# Validation messages
def E_REQUIRED(f):
    return f"Campo '{f}' obrigat\u00f3rio"

def E_PATTERN(f, v, p):
    return f"Campo '{f}' com valor '{v}' n\u00e3o corresponde ao padr\u00e3o '{p}'"

def E_ENUM(f, v, opts):
    return f"Campo '{f}' com valor '{v}' n\u00e3o est\u00e1 entre os valores permitidos: {opts}"

def E_CONDITIONAL(fr, ft, tv):
    return (
        f"O campo '{fr}' tornou-se obrigat\u00f3rio porque o campo '{ft}' foi informado com o valor '{tv}'."
    )

def E_MAX_ITEMS(f, v, inst):
    return (
        f"Quando o valor do campo '{f}' for '{v}', apenas ele deve constar na lista. Foir informado '{inst}'."
    )

M_001 = "Opera\u00e7\u00e3o conclu\u00edda"
W_001 = "Aviso"

# API messages
USER_CREATED = "user created"
ERR_USERNAME_PASSWORD_REQUIRED = "username and password required"
ERR_USERNAME_EXISTS = "username already exists"

# Exception messages
LOGIN_FAIL = "Falha na autentica\u00e7\u00e3o do SIScan."

def MENU_ACTION_NOT_FOUND(menu, action):
    return f"Menu '{menu}' com a\u00e7\u00e3o '{action}' n\u00e3o encontrado no SIScan."

def MENU_NOT_FOUND(menu):
    return f"Menu '{menu}' n\u00e3o encontrado no SIScan."

MENU_OR_ACTION_NOT_FOUND = "Menu ou ac\u00e7\u00e3o de menu n\u00e3o encontrado no SIScan."

def CARTAO_SUS_NOT_FOUND_VAL(cs):
    return f"N\u00e3o existe paciente com o Cart\u00e3o SUS informado: {cs}."

CARTAO_SUS_NOT_FOUND = "N\u00e3o existe paciente com o Cart\u00e3o SUS informado."
MULTIPLE_PATIENTS = (
    "Foram encontrados m\u00faltiplos pacientes na busca. A sele\u00e7\u00e3o n\u00e3o pode ser realizada automaticamente."
)

def XPATH_NOT_FOUND_VAL(xp):
    return f"Elemento com XPath '{xp}' n\u00e3o encontrado ou n\u00e3o resolv\u00edvel na p\u00e1gina do SIScan."

XPATH_NOT_FOUND = "Elemento n\u00e3o encontrado ou n\u00e3o resolv\u00edvel na p\u00e1gina do SIScan."

def FIELD_VALUE_NOT_FOUND(field, value):
    return (
        f"Valor '{value}' n\u00e3o encontrado na lista de op\u00e7\u00f5es v\u00e1lidas para o campo '{field}'."
    )

def INVALID_FIELD_VALUE_OPTIONS(field, value, opts):
    return (
        f"O valor '{value}' fornecido para o campo '{field}' n\u00e3o consta na lista de op\u00e7\u00f5es v\u00e1lidas. Op\u00e7\u00f5es v\u00e1lidas: {', '.join(opts)}."
    )

def FIELD_REQUIRED(field):
    return f"O campo '{field}' deve ser informado."

# Other domain messages
MENU_ACCESS_TIMEOUT = "Menu n\u00e3o localizado ap\u00f3s m\u00faltiplas tentativas."
ANO_MAMOGRAFIA_REQUIRED = (
    "Campos 'Ano' de 'QUANDO FEZ A \u00daLTIMA MAMOGRAFIA?' do card 'FEZ MAMOGRAFIA ALGUMA VEZ?' \u00e9 obrigat\u00f3rio."
)
ANO_RADIOTERAPIA_REQUIRED = "Campos de ano da radioterapia obrigat\u00f3rios conforme a localiza\u00e7\u00e3o."
CARTAO_SUS_NAO_INFORMADO = "Cart\u00e3o SUS n\u00e3o informado."

__all__ = [name for name in globals() if name.isupper()]
