# Validation messages
E_REQUIRED = lambda f: f"Campo '{f}' obrigat\u00f3rio"
E_PATTERN = lambda f, v, p: f"Campo '{f}' com valor '{v}' n\u00e3o corresponde ao padr\u00e3o '{p}'"
E_ENUM = lambda f, v, opts: f"Campo '{f}' com valor '{v}' n\u00e3o est\u00e1 entre os valores permitidos: {opts}"
E_CONDITIONAL = lambda fr, ft, tv: (
    f"O campo '{fr}' tornou-se obrigat\u00f3rio porque o campo '{ft}' foi informado com o valor '{tv}'."
)
E_MAX_ITEMS = lambda f, v, inst: (
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
MENU_ACTION_NOT_FOUND = lambda menu, action: f"Menu '{menu}' com a\u00e7\u00e3o '{action}' n\u00e3o encontrado no SIScan."
MENU_NOT_FOUND = lambda menu: f"Menu '{menu}' n\u00e3o encontrado no SIScan."
MENU_OR_ACTION_NOT_FOUND = "Menu ou ac\u00e7\u00e3o de menu n\u00e3o encontrado no SIScan."
CARTAO_SUS_NOT_FOUND_VAL = lambda cs: f"N\u00e3o existe paciente com o Cart\u00e3o SUS informado: {cs}."
CARTAO_SUS_NOT_FOUND = "N\u00e3o existe paciente com o Cart\u00e3o SUS informado."
MULTIPLE_PATIENTS = (
    "Foram encontrados m\u00faltiplos pacientes na busca. A sele\u00e7\u00e3o n\u00e3o pode ser realizada automaticamente."
)
XPATH_NOT_FOUND_VAL = lambda xp: f"Elemento com XPath '{xp}' n\u00e3o encontrado ou n\u00e3o resolv\u00edvel na p\u00e1gina do SIScan."
XPATH_NOT_FOUND = "Elemento n\u00e3o encontrado ou n\u00e3o resolv\u00edvel na p\u00e1gina do SIScan."
FIELD_VALUE_NOT_FOUND = lambda field, value: (
    f"Valor '{value}' n\u00e3o encontrado na lista de op\u00e7\u00f5es v\u00e1lidas para o campo '{field}'."
)
INVALID_FIELD_VALUE_OPTIONS = lambda field, value, opts: (
    f"O valor '{value}' fornecido para o campo '{field}' n\u00e3o consta na lista de op\u00e7\u00f5es v\u00e1lidas. Op\u00e7\u00f5es v\u00e1lidas: {', '.join(opts)}."
)
FIELD_REQUIRED = lambda field: f"O campo '{field}' deve ser informado."

# Other domain messages
MENU_ACCESS_TIMEOUT = "Menu n\u00e3o localizado ap\u00f3s m\u00faltiplas tentativas."
ANO_MAMOGRAFIA_REQUIRED = (
    "Campos 'Ano' de 'QUANDO FEZ A \u00daLTIMA MAMOGRAFIA?' do card 'FEZ MAMOGRAFIA ALGUMA VEZ?' \u00e9 obrigat\u00f3rio."
)
ANO_RADIOTERAPIA_REQUIRED = "Campos de ano da radioterapia obrigat\u00f3rios conforme a localiza\u00e7\u00e3o."
CARTAO_SUS_NAO_INFORMADO = "Cart\u00e3o SUS n\u00e3o informado."

__all__ = [name for name in globals() if name.isupper()]
