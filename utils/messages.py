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
